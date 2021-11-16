import logging
import numpy as np
from typing import Optional, Union

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions.dirichlet import Dirichlet

from seqlbtoolkit.data import label_to_span
from seqlbtoolkit.eval import Metric
from utils.math import (
    log_matmul,
    log_maxmul,
    validate_prob,
    logsumexp,
    prob_scaling,
    entity_emiss_diag,
    entity_emiss_o,
    entity_emiss_nondiag
)
from .args import PriorConfig

logger = logging.getLogger(__name__)


class DirCHMMMetric(Metric):
    def __init__(self,
                 conc: Optional[Union[torch.Tensor, np.ndarray]] = None,
                 conc_batch: Optional[Union[torch.Tensor, np.ndarray]] = None):
        super(DirCHMMMetric, self).__init__()
        self.conc = conc
        self.conc_batch = conc_batch


class NeuralModule(nn.Module):
    def __init__(self,
                 config: PriorConfig):
        super(NeuralModule, self).__init__()

        self._d_emb = config.d_emb  # embedding dimension
        self._d_hidden = config.d_hidden
        self._n_src = config.n_src
        self._d_obs = config.d_obs
        self._device = config.device

        self._ent_exp1 = config.diag_exp_t1
        self._ent_exp2 = config.diag_exp_t2
        self._nondiag_exp = config.nondiag_exp

        self._use_src_prior = config.use_src_prior

        self._neural_transition = nn.Linear(self._d_emb, self._d_hidden * self._d_hidden)

        self._emission_2o = nn.Linear(self._d_emb, self._n_src)
        # TODO: currently entity-based. Can be modified to token-based
        self._emission_2e = nn.Linear(self._d_emb, self._n_src * config.n_entity)
        self._concentration_base = config.dirichlet_concentration_base
        self._concentration_range = config.dirichlet_concentration_max - config.dirichlet_concentration_base
        self._source_softmax = nn.Softmax(dim=-2)
        self._sigmoid = nn.Sigmoid()

        # define indices for elements
        self._e2e_diag_idx = torch.eye(self._d_obs, dtype=torch.bool)
        self._e2e_diag_idx[0, 0] = False
        self._e2e_nondiag_idx = ~torch.eye(self._d_obs, dtype=torch.bool)
        self._e2e_nondiag_idx[0, :] = False
        self._e2e_nondiag_idx[:, 0] = False

        self._init_parameters()

    # noinspection PyTypeChecker
    def forward(self,
                embs: torch.Tensor,
                temperature: Optional[int] = 1.0):
        batch_size, max_seq_length, _ = embs.size()
        trans_temp = self._neural_transition(embs).view(
            batch_size, max_seq_length, self._d_hidden, self._d_hidden
        )
        nn_trans = torch.softmax(trans_temp / temperature, dim=-1)

        # get Dirichlet parameters
        # assume the reliability of a source remains constant across the whole sequence
        # TODO: incorporate token-dependency
        # predict the concentration parameter for o2o from sequence embedding; batch_size X n_src
        conc_o2o = self._sigmoid(self._emission_2o(embs[:, 0, :]))
        # predict the concentration parameter for e2e; batch_size X n_src X n_entity
        conc_e2e = self._emission_2e(embs[:, 0, :]).view([batch_size, self._n_src, -1])

        if self._use_src_prior:
            conc_e2e = torch.sigmoid(conc_e2e)
        else:
            conc_e2e = self._source_softmax(conc_e2e)
        # scale up the result
        conc_e2e = prob_scaling(conc_e2e, 1 / self._n_src, self._ent_exp1, self._ent_exp2)

        # TODO: entropy regularization
        # TODO: prior regularization

        # initialize the dirichlet parameter matrix; shape: batch_size X n_src X d_obs X d_obs
        diric_params = torch.zeros(
            [batch_size, self._n_src, self._d_obs, self._d_obs], device=self._device
        ) + 1E-9  # Add a small value to guarantee positivity. Should not be necessary but nice to have
        # assign the first row
        diric_params[:, :, 0, 0] = conc_o2o
        diric_params[:, :, 0, 1:] = ((1 - conc_o2o) / (self._d_obs - 1)).unsqueeze(-1)

        # assign the e2e emission probabilities
        diric_params[:, :, self._e2e_diag_idx] = \
            entity_emiss_diag(conc_e2e).repeat_interleave(2, dim=-1)

        # get non-diagonal e2e emissions (heuristic)
        # Rayleigh distribution is hard to design. Use piecewise polynomial instead
        turning_point = 0.5 / self._d_obs

        non_diag_values = entity_emiss_nondiag(
            x=conc_e2e, n_lbs=self._d_obs, tp=turning_point, exp_term=self._nondiag_exp
        ).detach()
        diric_params[:, :, self._e2e_nondiag_idx] = non_diag_values.repeat_interleave(2*(self._d_obs-2), dim=-1)

        # the first column other than [0,0]
        e2o_values = entity_emiss_o(
            x=conc_e2e, n_lbs=self._d_obs, tp=turning_point, exp_term=self._nondiag_exp
        )
        diric_params[:, :, 1:, 0] = e2o_values.repeat_interleave(2, dim=-1)

        ranged_diric_params = diric_params * self._concentration_range + self._concentration_base
        # construct dirichlet distribution
        dirichlet_distr = Dirichlet(ranged_diric_params)
        # sample from distribution
        dirichlet_emiss = dirichlet_distr.rsample()

        return nn_trans, dirichlet_emiss, (conc_o2o, conc_e2e)

    def _init_parameters(self):
        nn.init.xavier_uniform_(self._neural_transition.weight.data)
        nn.init.xavier_uniform_(self._emission_2o.weight.data)
        nn.init.xavier_uniform_(self._emission_2e.weight.data)


class PriorCHMM(nn.Module):

    def __init__(self,
                 config: PriorConfig,
                 state_prior=None,
                 trans_matrix=None,
                 emiss_matrix=None):
        super(PriorCHMM, self).__init__()

        self._n_src = config.n_src
        self._d_obs = config.d_obs  # number of possible obs_set
        self._d_hidden = config.d_hidden  # number of states

        self._trans_weight = config.trans_nn_weight
        self._emiss_weight = config.emiss_nn_weight

        self._device = config.device

        self._nn_module = NeuralModule(config)

        # initialize unnormalized state-prior, transition and emission matrices
        self._initialize_model(
            state_prior=state_prior, trans_matrix=trans_matrix, emiss_matrix=emiss_matrix
        )
        self.to(self._device)

        self._inter_results = DirCHMMMetric()

    @property
    def log_trans(self):
        try:
            return self._log_trans
        except NameError:
            logger.error('DirCHMM.log_trans is not defined!')
            return None

    @property
    def log_emiss(self):
        try:
            return self._log_emiss
        except NameError:
            logger.error('DirCHMM.log_emiss is not defined!')
            return None

    @property
    def inter_results(self) -> "DirCHMMMetric":
        return self._inter_results

    def pop_inter_results(self) -> "DirCHMMMetric":
        result = self._inter_results
        self._inter_results = DirCHMMMetric()
        return result

    def _initialize_model(self,
                          state_prior: torch.Tensor,
                          trans_matrix: torch.Tensor,
                          emiss_matrix: torch.Tensor):
        """
        Initialize model parameters

        Parameters
        ----------
        state_prior: state prior (pi)
        trans_matrix: transition matrices
        emiss_matrix: emission matrices

        Returns
        -------
        self
        """

        logger.info('Initializing Dirichlet CHMM...')

        if state_prior is None:
            priors = torch.zeros(self._d_hidden, device=self._device) + 1E-3
            priors[0] = 1
            self._state_priors = nn.Parameter(torch.log(priors))
        else:
            state_prior.to(self._device)
            priors = validate_prob(state_prior, dim=0)
            self._state_priors = nn.Parameter(torch.log(priors))

        if trans_matrix is None:
            self._unnormalized_trans = nn.Parameter(torch.randn(self._d_hidden, self._d_hidden, device=self._device))
        else:
            trans_matrix.to(self._device)
            trans_matrix = validate_prob(trans_matrix)
            # We may want to use softmax later, so we put here a log to counteract the effact
            self._unnormalized_trans = nn.Parameter(torch.log(trans_matrix))

        if emiss_matrix is None:
            self._unnormalized_emiss = nn.Parameter(
                torch.zeros(self._n_src, self._d_hidden, self._d_obs, device=self._device)
            )
        else:
            emiss_matrix.to(self._device)
            emiss_matrix = validate_prob(emiss_matrix)
            # We may want to use softmax later, so we put a log here
            self._unnormalized_emiss = nn.Parameter(torch.log(emiss_matrix))

        logger.info("Dirichlet CHMM initialized!")

        return self

    def _initialize_states(self,
                           embs: torch.Tensor,
                           obs: torch.Tensor,
                           temperature: Optional[int] = 1.0,
                           normalize_observation: Optional[bool] = True):
        """
        Initialize inference states. Should be called before forward inference.

        Parameters
        ----------
        embs: token embeddings
        obs: observations
        temperature: softmax temperature
        normalize_observation: whether to normalize observations

        Returns
        -------
        self
        """
        # normalize and put the probabilities into the log domain
        batch_size, max_seq_length, n_src, _ = obs.size()
        self._log_state_priors = torch.log_softmax(self._state_priors / temperature, dim=-1)
        trans = torch.softmax(self._unnormalized_trans / temperature, dim=-1)
        emiss = torch.softmax(self._unnormalized_emiss / temperature, dim=-1)

        # get neural transition and emission matrices
        # TODO: we can add layer-norm later to see what happens
        nn_trans, nn_emiss, conc = self._nn_module(embs)

        self._log_trans = torch.log((1 - self._trans_weight) * trans + self._trans_weight * nn_trans)

        if nn_emiss is not None:
            self._log_emiss = torch.log((1 - self._emiss_weight) * emiss.unsqueeze(0) + self._emiss_weight * nn_emiss)

            # save the record
            conc_comb = torch.concat((conc[0].unsqueeze(-1), conc[1]), dim=-1)
            self._inter_results.conc_batch = conc_comb

            if self._inter_results.conc is None:
                self._inter_results.conc = conc_comb.detach().cpu().numpy()
            else:
                self._inter_results.conc = np.r_[self._inter_results.conc, conc_comb.detach().cpu().numpy()]

        else:
            self._log_emiss = torch.log(emiss)

        # if at least one source observes an entity at a position, set the probabilities of other sources to
        # the mean value (so that they will not affect the prediction)
        # maybe we can also set them all to 0?
        # [10/20/2020] The current version works fine. No need to change for now.
        # [10/20/2020] Pack this process into an if branch
        # TODO: this should not be necessary with Dirichlet emission
        if normalize_observation:
            lbs = obs.argmax(dim=-1)
            # at least one source observes an entity
            entity_idx = lbs.sum(dim=-1) > 1E-6
            # the sources that do not observe any entity
            no_entity_idx = lbs <= 1E-6
            no_obs_src_idx = entity_idx.unsqueeze(-1) * no_entity_idx
            subsitute_prob = torch.zeros_like(obs[0, 0, 0])
            subsitute_prob[0] = 0.01
            subsitute_prob[1:] = 0.99 / self._d_obs
            obs[no_obs_src_idx] = subsitute_prob

        # Calculate the emission probabilities in one time, so that we don't have to compute this repeatedly
        # log-domain subtract is regular-domain divide
        self._log_emiss_evidence = log_matmul(
            self._log_emiss.unsqueeze(1), torch.log(obs).unsqueeze(-1)
        ).squeeze(-1).sum(dim=-2)

        self._log_alpha = torch.zeros([batch_size, max_seq_length, self._d_hidden], device=self._device)
        self._log_beta = torch.zeros([batch_size, max_seq_length, self._d_hidden], device=self._device)
        # Gamma can be readily computed and need no initialization
        self._log_gamma = None
        # only values in 1:max_seq_length are valid. The first state is a dummy
        self._log_xi = torch.zeros([batch_size, max_seq_length, self._d_hidden, self._d_hidden], device=self._device)
        return self

    def _forward_step(self, t):
        # initial alpha state
        if t == 0:
            log_alpha_t = self._log_state_priors + self._log_emiss_evidence[:, t, :]
        # do the forward step
        else:
            log_alpha_t = self._log_emiss_evidence[:, t, :] + \
                          log_matmul(self._log_alpha[:, t - 1, :].unsqueeze(1), self._log_trans[:, t, :, :]).squeeze(1)

        # normalize the result
        normalized_log_alpha_t = log_alpha_t - log_alpha_t.logsumexp(dim=-1, keepdim=True)
        return normalized_log_alpha_t

    def _backward_step(self, t):
        # do the backward step
        # beta is not a distribution, so we do not need to normalize it
        log_beta_t = log_matmul(
            self._log_trans[:, t, :, :],
            (self._log_emiss_evidence[:, t, :] + self._log_beta[:, t + 1, :]).unsqueeze(-1)
        ).squeeze(-1)
        return log_beta_t

    def _forward_backward(self, seq_lengths):
        max_seq_length = seq_lengths.max().item()
        # calculate log alpha
        for t in range(0, max_seq_length):
            self._log_alpha[:, t, :] = self._forward_step(t)

        # calculate log beta
        # The last beta state beta[:, -1, :] = log1 = 0, so no need to re-assign the value
        for t in range(max_seq_length - 2, -1, -1):
            self._log_beta[:, t, :] = self._backward_step(t)
        # shift the output (since beta is calculated in backward direction,
        # we need to shift each instance in the batch according to its length)
        shift_distances = seq_lengths - max_seq_length
        self._log_beta = torch.stack(
            [torch.roll(beta, s.item(), 0) for beta, s in zip(self._log_beta, shift_distances)]
        )
        return None

    def _compute_xi(self, t):
        temp_1 = self._log_emiss_evidence[:, t, :] + self._log_beta[:, t, :]
        temp_2 = log_matmul(self._log_alpha[:, t - 1, :].unsqueeze(-1), temp_1.unsqueeze(1))
        log_xi_t = self._log_trans[:, t, :, :] + temp_2
        return log_xi_t

    def _expected_complete_log_likelihood(self, seq_lengths):
        batch_size = len(seq_lengths)
        max_seq_length = seq_lengths.max().item()

        # calculate expected sufficient statistics: gamma_t(j) = P(z_t = j|x_{1:T})
        self._log_gamma = self._log_alpha + self._log_beta
        # normalize as gamma is a distribution
        log_gamma = self._log_gamma - self._log_gamma.logsumexp(dim=-1, keepdim=True)

        # calculate expected sufficient statistics: psi_t(i, j) = P(z_{t-1}=i, z_t=j|x_{1:T})
        for t in range(1, max_seq_length):
            self._log_xi[:, t, :, :] = self._compute_xi(t)
        stabled_norm_term = logsumexp(self._log_xi[:, 1:, :, :].view(batch_size, max_seq_length - 1, -1), dim=-1)\
            .view(batch_size, max_seq_length-1, 1, 1)
        log_xi = self._log_xi[:, 1:, :, :] - stabled_norm_term

        # calculate the expected complete data log likelihood
        log_prior = torch.sum(torch.exp(log_gamma[:, 0, :]) * self._log_state_priors, dim=-1)
        log_prior = log_prior.mean()
        # sum over j, k
        log_tran = torch.sum(torch.exp(log_xi) * self._log_trans[:, 1:, :, :], dim=[-2, -1])
        # sum over valid time steps, and then average over batch. Note this starts from t=2
        log_tran = torch.mean(torch.stack([inst[:length].sum() for inst, length in zip(log_tran, seq_lengths-1)]))
        # same as above
        log_emis = torch.sum(torch.exp(log_gamma) * self._log_emiss_evidence, dim=-1)
        log_emis = torch.mean(torch.stack([inst[:length].sum() for inst, length in zip(log_emis, seq_lengths)]))
        log_likelihood = log_prior + log_tran + log_emis

        return log_likelihood

    def forward(self, emb, obs, seq_lengths, normalize_observation=True):
        # the row of obs should be one-hot or at least sum to 1
        # assert (obs.sum(dim=-1) == 1).all()

        batch_size, max_seq_length, n_src, n_obs = obs.size()
        assert n_obs == self._d_obs
        assert n_src == self._n_src

        # Initialize alpha, beta and xi
        self._initialize_states(embs=emb, obs=obs, normalize_observation=normalize_observation)
        self._forward_backward(seq_lengths=seq_lengths)
        log_likelihood = self._expected_complete_log_likelihood(seq_lengths=seq_lengths)
        return log_likelihood

    def viterbi(self, emb, obs, seq_lengths, normalize_observation=True):
        """
        Find argmax_z log p(z|obs) for each (obs) in the batch.
        """
        batch_size = len(seq_lengths)
        max_seq_length = seq_lengths.max().item()

        # initialize states
        self._initialize_states(embs=emb, obs=obs, normalize_observation=normalize_observation)
        # maximum probabilities
        log_delta = torch.zeros([batch_size, max_seq_length, self._d_hidden], device=self._device)
        # most likely previous state on the most probable path to z_t = j. a[0] is undefined.
        pre_states = torch.zeros([batch_size, max_seq_length, self._d_hidden], dtype=torch.long, device=self._device)

        # the initial delta state
        log_delta[:, 0, :] = self._log_state_priors + self._log_emiss_evidence[:, 0, :]
        for t in range(1, max_seq_length):
            # udpate delta and a. The location of the emission probabilities does not matter
            max_log_prob, argmax_val = log_maxmul(
                log_delta[:, t-1, :].unsqueeze(1),
                self._log_trans[:, t, :, :] + self._log_emiss_evidence[:, t, :].unsqueeze(1)
            )
            log_delta[:, t, :] = max_log_prob.squeeze(1)
            pre_states[:, t, :] = argmax_val.squeeze(1)

        # The terminal state
        batch_max_log_prob = list()
        batch_z_t_star = list()

        for l_delta, length in zip(log_delta, seq_lengths):
            max_log_prob, z_t_star = l_delta[length-1, :].max(dim=-1)
            batch_max_log_prob.append(max_log_prob)
            batch_z_t_star.append(z_t_star)

        # Trace back
        batch_z_star = [[z_t_star.item()] for z_t_star in batch_z_t_star]
        for p_states, z_star, length in zip(pre_states, batch_z_star, seq_lengths):
            for t in range(length-2, -1, -1):
                z_t = p_states[t+1, z_star[0]].item()
                z_star.insert(0, z_t)

        # compute the smoothed marginal p(z_t = j | obs_{1:T})
        self._forward_backward(seq_lengths)
        log_marginals = self._log_alpha + self._log_beta
        norm_marginals = torch.exp(log_marginals - logsumexp(log_marginals, dim=-1, keepdim=True))
        batch_marginals = list()
        for marginal, length in zip(norm_marginals, seq_lengths):
            mgn_list = marginal[:length].detach().cpu().numpy()
            batch_marginals.append(mgn_list)

        return batch_z_star, batch_marginals

    def annotate(self, emb, obs, seq_lengths, label_types, normalize_observation=True):
        batch_label_indices, batch_probs = self.viterbi(
            emb, obs, seq_lengths, normalize_observation=normalize_observation
        )
        batch_labels = [[label_types[lb_index] for lb_index in label_indices]
                        for label_indices in batch_label_indices]

        # For batch_spans, we are going to compare them with the true spans,
        # and the true spans is already shifted, so we do not need to shift predicted spans back
        batch_spans = list()
        batch_scored_spans = list()
        for labels, probs, indices in zip(batch_labels, batch_probs, batch_label_indices):
            spans = label_to_span(labels)
            batch_spans.append(spans)

            ps = [p[s] for p, s in zip(probs, indices[1:])]
            scored_spans = dict()
            for k, v in spans.items():
                if k == (0, 1):
                    continue
                start = k[0] - 1 if k[0] > 0 else 0
                end = k[1] - 1
                score = np.mean(ps[start:end])
                scored_spans[(start, end)] = [(v, score)]
            batch_scored_spans.append(scored_spans)

        return batch_spans, (batch_scored_spans, batch_probs)
