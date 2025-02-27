# coding=utf-8
""" Train the conditional hidden Markov model with alternate training"""

import logging
import os
import sys
import gc
import torch
from datetime import datetime

from transformers import (
    HfArgumentParser,
    set_seed,
)

# submodule dependencies
from seqlbtoolkit.io import set_logging, logging_args
from seqlbtoolkit.data import span_to_label, label_to_span
# in-project dependencies
from src.chmm.dataset import CHMMBaseDataset, collate_fn
from src.chmm.train import CHMMTrainer
from src.bert.dataset import BertNERDataset
from src.bert.train import BertTrainer
from src.alt.args import AltArguments, AltConfig

logger = logging.getLogger(__name__)


def chmm_train(args: AltArguments):
    set_seed(args.seed)
    config = AltConfig().from_args(args)

    # setup CHMM datasets
    chmm_training_dataset = chmm_valid_dataset = chmm_test_dataset = None
    if args.train_path:
        logger.info('Loading training dataset for CHMM...')
        chmm_training_dataset = CHMMBaseDataset().load_file(
            file_path=args.train_path,
            config=config
        )
    if args.valid_path:
        logger.info('Loading validation dataset for CHMM...')
        chmm_valid_dataset = CHMMBaseDataset().load_file(
            file_path=args.valid_path,
            config=config
        )
    if args.test_path:
        logger.info('Loading test dataset for CHMM...')
        chmm_test_dataset = CHMMBaseDataset().load_file(
            file_path=args.test_path,
            config=config
        )

    # create output dir if it does not exist
    if not os.path.isdir(args.output_dir):
        os.makedirs(os.path.abspath(args.output_dir))

    # --- Phase I ---
    logger.info("--- Phase I training ---")

    chmm_trainer = CHMMTrainer(
        config=config,
        collate_fn=collate_fn,
        training_dataset=chmm_training_dataset,
        valid_dataset=chmm_valid_dataset,
        test_dataset=chmm_test_dataset,
    ).initialize_trainer()

    if args.train_path:
        logger.info("Start training CHMM.")
        valid_results = chmm_trainer.train()
    else:
        chmm_trainer.load(os.path.join(args.output_dir, 'chmm.bin'), load_optimizer_and_scheduler=True)
        valid_results = None

    if args.test_path:
        logger.info("Start testing CHMM.")

        test_metrics = chmm_trainer.test()

        logger.info("Test results:")
        for k, v in test_metrics.items():
            logger.info(f"\t{k}: {v:.4f}")
    else:
        test_metrics = None

    result_file = os.path.join(args.output_dir, 'chmm-results-p1.txt')
    logger.info(f"Writing results to {result_file}")
    with open(result_file, 'w') as f:
        if valid_results is not None:
            for i in range(len(valid_results)):
                f.write(f"[Epoch {i + 1}]\n")
                for k, v in valid_results.items(i):
                    f.write(f"  {k}: {v:.4f}\n")
                f.write('\n')
        if test_metrics is not None:
            f.write(f"[Test]\n")
            for k, v in test_metrics.items():
                f.write(f"  {k}: {v:.4f}\n")
            f.write('\n')

    chmm_pred_lbs_train, chmm_pred_probs_train = chmm_trainer.predict(chmm_training_dataset)
    # make sure the predicted labels are valid spans (do not start with I-)
    chmm_pred_lbs_train = [span_to_label(label_to_span(lbs), tks) for lbs, tks in
                           zip(chmm_pred_lbs_train, chmm_training_dataset.text)]

    if config.pass_soft_labels:
        chmm_out = chmm_pred_probs_train
    else:
        chmm_out = chmm_pred_lbs_train

    logger.info("Collecting garbage.")
    gc.collect()
    torch.cuda.empty_cache()

    bert_training_dataset = bert_valid_dataset = bert_test_dataset = None
    if args.train_path:
        logger.info('Constructing training dataset for BERT...')
        bert_training_dataset = BertNERDataset(
            text=[txt[1:] for txt in chmm_training_dataset.text],  # remove the sentence header
            lbs=[lbs[1:] for lbs in chmm_out]  # use the predicted labels as BERT training objective
        ).encode_text_and_lbs(config=config)
    if args.valid_path:
        logger.info('Constructing validation dataset for BERT...')
        bert_valid_dataset = BertNERDataset(
            text=[txt[1:] for txt in chmm_valid_dataset.text],  # remove the sentence header
            lbs=[lbs[1:] for lbs in chmm_valid_dataset.lbs]  # use true labels for validation and test
        ).encode_text_and_lbs(config=config)
    if args.test_path:
        logger.info('Constructing test dataset for BERT...')
        bert_test_dataset = BertNERDataset(
            text=[txt[1:] for txt in chmm_test_dataset.text],  # remove the sentence header
            lbs=[lbs[1:] for lbs in chmm_test_dataset.lbs]
        ).encode_text_and_lbs(config=config)

    bert_trainer = BertTrainer(
        config=config,
        training_dataset=bert_training_dataset,
        valid_dataset=bert_valid_dataset,
        test_dataset=bert_test_dataset,
    ).initialize_trainer()

    if args.train_path:
        logger.info("Start training Bert...")
        valid_results = bert_trainer.train()
    else:
        bert_trainer.load(args.output_dir, load_optimizer_and_scheduler=True)
        valid_results = None

    if args.test_path:
        logger.info("Start testing Bert...")
        test_metrics = bert_trainer.test()
    else:
        test_metrics = None

    result_file = os.path.join(args.output_dir, 'bert-results-p1.txt')
    logger.info(f"Writing results to {result_file}")
    with open(result_file, 'w') as f:
        if valid_results is not None:
            for i in range(len(valid_results)):
                f.write(f"[Epoch {i + 1}]\n")
                for k, v in valid_results.items(i):
                    f.write(f"  {k}: {v:.4f}\n")
                f.write('\n')
        if test_metrics is not None:
            f.write(f"[Test]\n")
            for k, v in test_metrics.items():
                f.write(f"  {k}: {v:.4f}\n")
            f.write('\n')

    logger.info("Collecting garbage.")
    gc.collect()
    torch.cuda.empty_cache()

    # --- Phase II ---
    logger.info("--- Phase II training ---")
    logger.info("Updating BERT training hyper-parameters")
    config.learning_rate /= 2
    config.num_em_train_epochs = config.num_phase2_em_train_epochs
    config.batch_gradient_descent = True
    bert_trainer.config = config

    for loop_i in range(config.num_phase2_loop):

        logger.info("Updating CHMM dataset...")

        if args.train_path:
            bert_pred_lbs_train, _ = bert_trainer.predict(bert_training_dataset)
            # make sure the predicted labels are valid spans (do not start with I-)
            bert_pred_lbs_train = [span_to_label(label_to_span(lbs), tks) for lbs, tks in
                                   zip(bert_pred_lbs_train, bert_training_dataset.text)]
            chmm_training_dataset.update_obs(bert_pred_lbs_train, 'BertLabels', config)

        if args.valid_path:
            bert_pred_lbs_valid, _ = bert_trainer.predict(bert_valid_dataset)
            bert_pred_lbs_valid = [span_to_label(label_to_span(lbs), tks) for lbs, tks in
                                   zip(bert_pred_lbs_valid, bert_valid_dataset.text)]
            chmm_valid_dataset.update_obs(bert_pred_lbs_valid, 'BertLabels', config)

        if args.test_path:
            bert_pred_lbs_test, _ = bert_trainer.predict(bert_test_dataset)
            bert_pred_lbs_test = [span_to_label(label_to_span(lbs), tks) for lbs, tks in
                                  zip(bert_pred_lbs_test, bert_test_dataset.text)]
            chmm_test_dataset.update_obs(bert_pred_lbs_test, 'BertLabels', config)

        chmm_trainer = CHMMTrainer(
            config=config,
            collate_fn=collate_fn,
            training_dataset=chmm_training_dataset,
            valid_dataset=chmm_valid_dataset,
            test_dataset=chmm_test_dataset,
        ).initialize_trainer()

        if args.train_path:
            logger.info("Start training CHMM.")
            valid_results = chmm_trainer.train()
        else:
            chmm_trainer.load(os.path.join(args.output_dir, 'chmm.bin'), load_optimizer_and_scheduler=True)
            valid_results = None

        if args.test_path:
            logger.info("Start testing CHMM.")
            test_metrics = chmm_trainer.test()

        else:
            test_metrics = None

        result_file = os.path.join(args.output_dir, f'chmm-results-p2.{loop_i+1}.txt')
        logger.info(f"Writing results to {result_file}")
        with open(result_file, 'w') as f:
            if valid_results is not None:
                for i in range(len(valid_results)):
                    f.write(f"[Epoch {i + 1}]\n")
                    for k, v in valid_results.items(i):
                        f.write(f"  {k}: {v:.4f}\n")
                    f.write('\n')
            if test_metrics is not None:
                f.write(f"[Test]\n")
                for k, v in test_metrics.items():
                    f.write(f"  {k}: {v:.4f}\n")
                f.write('\n')

        chmm_pred_lbs_train, chmm_pred_probs_train = chmm_trainer.predict(chmm_training_dataset)
        # make sure the predicted labels are valid spans (do not start with I-)
        chmm_pred_lbs_train = [span_to_label(label_to_span(lbs), tks) for lbs, tks in
                               zip(chmm_pred_lbs_train, chmm_training_dataset.text)]

        if config.pass_soft_labels:
            chmm_out = chmm_pred_probs_train
        else:
            chmm_out = chmm_pred_lbs_train

        logger.info("Collecting garbage.")
        gc.collect()
        torch.cuda.empty_cache()

        logger.info("Updating BERT dataset")
        if args.train_path:
            bert_training_dataset.lbs = [lbs[1:] for lbs in chmm_out]
            bert_training_dataset.encode_text_and_lbs(config=config)

        bert_trainer = BertTrainer(
            config=config,
            training_dataset=bert_training_dataset,
            valid_dataset=bert_valid_dataset,
            test_dataset=bert_test_dataset,
        ).initialize_trainer(
            model=bert_trainer.model,
            tokenizer=bert_trainer.tokenizer
        )

        if args.train_path:
            logger.info("Start training Bert...")
            valid_results = bert_trainer.train()
        else:
            bert_trainer.load(args.output_dir, load_optimizer_and_scheduler=True)
            valid_results = None

        if args.test_path:
            logger.info("Start testing Bert...")

            test_metrics = bert_trainer.test()

            logger.info("Test results:")
            for k, v in test_metrics.items():
                logger.info(f"\t{k}: {v:.4f}")
        else:
            test_metrics = None

        result_file = os.path.join(args.output_dir, f'bert-results-p2.{loop_i+1}.txt')
        logger.info(f"Writing results to {result_file}")
        with open(result_file, 'w') as f:
            if valid_results is not None:
                for i in range(len(valid_results)):
                    f.write(f"[Epoch {i + 1}]\n")
                    for k, v in valid_results.items(i):
                        f.write(f"  {k}: {v:.4f}\n")
                    f.write('\n')
            if test_metrics is not None:
                f.write(f"[Test]\n")
                for k, v in test_metrics.items():
                    f.write(f"  {k}: {v:.4f}\n")
                f.write('\n')

        logger.info("Collecting garbage.")
        gc.collect()
        torch.cuda.empty_cache()

    logger.info("Process finished!")


if __name__ == '__main__':

    _time = datetime.now().strftime("%m.%d.%y-%H.%M")
    _current_file_name = os.path.basename(__file__)
    if _current_file_name.endswith('.py'):
        _current_file_name = _current_file_name[:-3]

    # --- set up arguments ---
    parser = HfArgumentParser(AltArguments)
    if len(sys.argv) == 2 and sys.argv[1].endswith(".json"):
        # If we pass only one argument to the script and it's the path to a json file,
        # let's parse it to get our arguments.
        alt_args, = parser.parse_json_file(
            json_file=os.path.abspath(sys.argv[1])
        )
    else:
        alt_args, = parser.parse_args_into_dataclasses()

    # Setup logging
    if alt_args.log_dir is None:
        alt_args.log_dir = os.path.join('logs', f'{_current_file_name}', f'{_time}.log')

    set_logging(log_dir=alt_args.log_dir)
    logging_args(alt_args)

    chmm_train(args=alt_args)
