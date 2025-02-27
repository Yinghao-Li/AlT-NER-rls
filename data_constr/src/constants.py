"""
----------------------------------------------------------------------------------------------------------------------
List of Labels, annotation formats, and
prior probabilities used for source selection and model initialization
"""
import numpy as np

OntoNotes_LABELS = ['CARDINAL', "COMPANY", 'DATE', 'EVENT', 'FAC', 'GPE', 'LANGUAGE', 'LAW', 'LOC', 'MONEY',
                    'NORP', 'ORDINAL', 'ORG', 'PERCENT', 'PERSON', 'PRODUCT', 'QUANTITY', 'TIME', 'WORK_OF_ART']

CoNLL_LABELS = ["PER", "LOC", "ORG", "MISC"]

OntoNotes_BIO = ["O"] + ["%s-%s" % (bi, label) for label in OntoNotes_LABELS for bi in "BI"]
OntoNotes_INDICES = {label: i for i, label in enumerate(OntoNotes_BIO)}

CoNLL_BIO = ["O"] + ["%s-%s" % (bi, label) for label in CoNLL_LABELS for bi in "BI"]
CoNLL_INDICES = {label: i for i, label in enumerate(CoNLL_BIO)}

CoNLL_SOURCE_NAMES = ['BTC', 'BTC+c', 'SEC', 'SEC+c', 'company_type_detector', 'compound_detector',
                      'conll2003', 'conll2003+c', 'core_web_md', 'core_web_md+c', 'crunchbase_cased',
                      'crunchbase_uncased',
                      'date_detector',
                      'doc_history', 'doc_majority_cased', 'doc_majority_uncased', 'full_name_detector', 'geo_cased',
                      'geo_uncased',
                      'infrequent_compound_detector', 'infrequent_nnp_detector', 'infrequent_proper2_detector',
                      'infrequent_proper_detector',
                      'legal_detector', 'misc_detector', 'money_detector',
                      'multitoken_crunchbase_cased', 'multitoken_crunchbase_uncased', 'multitoken_geo_cased',
                      'multitoken_geo_uncased',
                      'multitoken_product_cased', 'multitoken_product_uncased', 'multitoken_wiki_cased',
                      'multitoken_wiki_small_cased',
                      'multitoken_wiki_small_uncased', 'multitoken_wiki_uncased', 'nnp_detector', 'number_detector',
                      'product_cased',
                      'product_uncased', 'proper2_detector', 'proper_detector', 'snips', 'time_detector', 'wiki_cased',
                      'wiki_small_cased',
                      'wiki_small_uncased', 'wiki_uncased']

# CoNLL_SOURCE_TO_KEEP = [
#     'BTC+c', 'core_web_md+c', 'crunchbase_uncased', 'wiki_uncased',
#     'geo_uncased', 'doc_majority_uncased'
# ]

CoNLL_SOURCE_TO_KEEP = ['BTC+c', 'SEC+c', 'core_web_md+c', 'crunchbase_cased', 'crunchbase_uncased',
                        'doc_majority_cased', 'doc_majority_uncased',
                        'full_name_detector', 'geo_cased', 'geo_uncased', 'misc_detector',
                        'wiki_cased', 'wiki_uncased']

# CoNLL_SOURCE_TO_KEEP = [
#     'BTC', 'BTC+c', 'SEC', 'SEC+c', 'company_type_detector', 'compound_detector',
#     'core_web_md', 'core_web_md+c', 'crunchbase_cased',
#     'crunchbase_uncased',
#     'date_detector',
#     'doc_history', 'doc_majority_cased', 'doc_majority_uncased', 'full_name_detector', 'geo_cased',
#     'geo_uncased',
#     'infrequent_compound_detector', 'infrequent_nnp_detector', 'infrequent_proper2_detector',
#     'infrequent_proper_detector',
#     'legal_detector', 'misc_detector', 'money_detector',
#     'multitoken_crunchbase_cased', 'multitoken_crunchbase_uncased', 'multitoken_geo_cased',
#     'multitoken_geo_uncased',
#     'multitoken_product_cased', 'multitoken_product_uncased', 'multitoken_wiki_cased',
#     'multitoken_wiki_small_cased',
#     'multitoken_wiki_small_uncased', 'multitoken_wiki_uncased', 'nnp_detector', 'number_detector',
#     'product_cased',
#     'product_uncased', 'proper2_detector', 'proper_detector', 'snips', 'time_detector', 'wiki_cased',
#     'wiki_small_cased',
#     'wiki_small_uncased', 'wiki_uncased'
# ]

NUMBER_NERS = ["CARDINAL", "DATE", "MONEY", "ORDINAL", "PERCENT", "QUANTITY", "TIME"]

# the numbers are precision and recall
CoNLL_SOURCE_PRIORS = {
    'BTC': {lbs: (0.4, 0.4) if lbs in ["COMPANY", "ORG", "PERSON", "GPE", "LOC"] else (0.3, 0.3) for lbs in
            OntoNotes_LABELS if
            lbs not in NUMBER_NERS},
    'BTC+c': {lbs: (0.5, 0.5) if lbs in ["COMPANY", "ORG", "PERSON", "GPE", "LOC", "MONEY"] else (0.4, 0.4) for lbs in
              OntoNotes_LABELS},
    'SEC': {lbs: (0.1, 0.1) if lbs in ["COMPANY", "ORG", "PERSON", "GPE", "LOC"] else (0.05, 0.05) for lbs in
            OntoNotes_LABELS if
            lbs not in NUMBER_NERS},
    'SEC+c': {lbs: (0.1, 0.1) if lbs in ["COMPANY", "ORG", "PERSON", "GPE", "LOC", "MONEY"] else (0.05, 0.05) for lbs in
              OntoNotes_LABELS},
    'company_type_detector': {'COMPANY': (0.9999, 0.4)},
    'compound_detector': {lbs: (0.7, 0.8) if lbs not in NUMBER_NERS else (0.01, 0.01) for lbs in OntoNotes_LABELS},
    'conll2003': {lbs: (0.7, 0.7) if lbs in ["COMPANY", "ORG", "PERSON", "GPE", "LOC"] else (0.4, 0.4)
                  for lbs in OntoNotes_LABELS if lbs not in NUMBER_NERS},
    'conll2003+c': {lbs: (0.7, 0.7) if lbs in ["COMPANY", "ORG", "PERSON", "GPE", "LOC"] else (0.4, 0.4)
                    for lbs in OntoNotes_LABELS},
    "core_web_md": {lbs: (0.9, 0.9) for lbs in OntoNotes_LABELS},
    "core_web_md+c": {lbs: (0.95, 0.95) for lbs in OntoNotes_LABELS},
    "crunchbase_cased": {lbs: (0.7, 0.6) for lbs in ["PERSON", "ORG", "COMPANY"]},
    "crunchbase_uncased": {lbs: (0.6, 0.7) for lbs in ["PERSON", "ORG", "COMPANY"]},
    'date_detector': {'DATE': (0.9, 0.9)},
    'doc_history': {lbs: (0.99, 0.4) for lbs in ["PERSON", "COMPANY"]},
    'doc_majority_cased': {lbs: (0.98, 0.4) for lbs in OntoNotes_LABELS},
    'doc_majority_uncased': {lbs: (0.95, 0.5) for lbs in OntoNotes_LABELS},
    'full_name_detector': {'PERSON': (0.9999, 0.4)},
    "geo_cased": {lbs: (0.8, 0.8) for lbs in ["GPE", "LOC"]},
    "geo_uncased": {lbs: (0.8, 0.8) for lbs in ["GPE", "LOC"]},
    'infrequent_compound_detector': {lbs: (0.7, 0.8) if lbs not in NUMBER_NERS else (0.01, 0.01) for lbs in
                                     OntoNotes_LABELS},
    'infrequent_nnp_detector': {lbs: (0.7, 0.8) if lbs not in NUMBER_NERS else (0.01, 0.01) for lbs in
                                OntoNotes_LABELS},
    'infrequent_proper2_detector': {lbs: (0.7, 0.8) if lbs not in NUMBER_NERS else (0.01, 0.01) for lbs in
                                    OntoNotes_LABELS},
    'infrequent_proper_detector': {lbs: (0.7, 0.8) if lbs not in NUMBER_NERS else (0.01, 0.01) for lbs in
                                   OntoNotes_LABELS},
    'legal_detector': {"LAW": (0.8, 0.8)},
    'misc_detector': {lbs: (0.7, 0.7) for lbs in ["NORP", "EVENT", "FAC", "GPE", "LANGUAGE"]},
    'money_detector': {'MONEY': (0.9, 0.9)},
    'multitoken_crunchbase_cased': {lbs: (0.8, 0.6) for lbs in ["PERSON", "ORG", "COMPANY"]},
    'multitoken_crunchbase_uncased': {lbs: (0.7, 0.7) for lbs in ["PERSON", "ORG", "COMPANY"]},
    'multitoken_geo_cased': {lbs: (0.8, 0.6) for lbs in ["GPE", "LOC"]},
    'multitoken_geo_uncased': {lbs: (0.7, 0.7) for lbs in ["GPE", "LOC"]},
    'multitoken_product_cased': {"PRODUCT": (0.8, 0.6)},
    'multitoken_product_uncased': {"PRODUCT": (0.7, 0.7)},
    'multitoken_wiki_cased': {lbs: (0.8, 0.6) for lbs in ["PERSON", "GPE", "LOC", "ORG", "COMPANY", "PRODUCT"]},
    'multitoken_wiki_small_cased': {lbs: (0.8, 0.6) for lbs in ["PERSON", "GPE", "LOC", "ORG", "COMPANY", "PRODUCT"]},
    'multitoken_wiki_small_uncased': {lbs: (0.7, 0.7) for lbs in ["PERSON", "GPE", "LOC", "ORG", "COMPANY", "PRODUCT"]},
    'multitoken_wiki_uncased': {lbs: (0.7, 0.7) for lbs in ["PERSON", "GPE", "LOC", "ORG", "COMPANY", "PRODUCT"]},
    'nnp_detector': {lbs: (0.8, 0.8) if lbs not in NUMBER_NERS else (0.01, 0.01) for lbs in OntoNotes_LABELS},
    "number_detector": {lbs: (0.9, 0.9) for lbs in ["CARDINAL", "ORDINAL", "QUANTITY", "PERCENT"]},
    'product_cased': {"PRODUCT": (0.7, 0.6)},
    'product_uncased': {"PRODUCT": (0.6, 0.7)},
    'proper2_detector': {lbs: (0.6, 0.8) if lbs not in NUMBER_NERS else (0.01, 0.01) for lbs in OntoNotes_LABELS},
    'proper_detector': {lbs: (0.6, 0.8) if lbs not in NUMBER_NERS else (0.01, 0.01) for lbs in OntoNotes_LABELS},
    "snips": {lbs: (0.8, 0.8) for lbs in ["DATE", "TIME", "PERCENT", "CARDINAL", "ORDINAL", "MONEY"]},
    'time_detector': {'TIME': (0.9, 0.9)},
    'wiki_cased': {lbs: (0.6, 0.5) for lbs in ["PERSON", "GPE", "LOC", "ORG", "COMPANY", "PRODUCT"]},
    'wiki_small_cased': {lbs: (0.7, 0.6) for lbs in ["PERSON", "GPE", "LOC", "ORG", "COMPANY", "PRODUCT"]},
    'wiki_small_uncased': {lbs: (0.6, 0.7) for lbs in ["PERSON", "GPE", "LOC", "ORG", "COMPANY", "PRODUCT"]},
    'wiki_uncased': {lbs: (0.5, 0.6) for lbs in ["PERSON", "GPE", "LOC", "ORG", "COMPANY", "PRODUCT"]}}

# In some rare cases (due to specialisations of corrections of labels), we also need to add some other labels
for lb_source in ["BTC", "BTC+c", "SEC", "SEC+c", "conll2003", "conll2003+c"]:
    CoNLL_SOURCE_PRIORS[lb_source].update({lbs: (0.8, 0.01) for lbs in NUMBER_NERS})

OUT_RECALL = 0.9
OUT_PRECISION = 0.8

"""
----------------------------------------------------------------------------------------------------------------------
Evaluation-related constants
"""

CoNLL_MAPPINGS = {"PERSON": "PER", "COMPANY": "ORG", "GPE": "LOC", 'EVENT': "MISC", 'FAC': "MISC", 'LANGUAGE': "MISC",
                  'LAW': "MISC", 'NORP': "MISC", 'PRODUCT': "MISC", 'WORK_OF_ART': "MISC"}

CONLL_SRC_PRIORS = dict()
for src, priors in CoNLL_SOURCE_PRIORS.items():
    transferred_lbs = dict()
    for lb_name, ps in priors.items():
        norm_lb = CoNLL_MAPPINGS.get(lb_name, lb_name)
        if norm_lb not in CoNLL_LABELS:
            continue
        if norm_lb not in transferred_lbs:
            transferred_lbs[norm_lb] = [list(), list()]
        transferred_lbs[norm_lb][0].append(ps[0])
        transferred_lbs[norm_lb][1].append(ps[1])
    for norm_lb in transferred_lbs:
        transferred_lbs[norm_lb][0] = np.mean(transferred_lbs[norm_lb][0])
        transferred_lbs[norm_lb][1] = np.mean(transferred_lbs[norm_lb][1])
        transferred_lbs[norm_lb] = tuple(transferred_lbs[norm_lb])
    CONLL_SRC_PRIORS[src] = transferred_lbs

NCBI_LABELS = ['DISEASE']
NCBI_BIO = ["O"] + ["%s-%s" % (bi, label) for label in NCBI_LABELS for bi in "BI"]
NCBI_INDICES = {label: i for i, label in enumerate(NCBI_BIO)}

NCBI_SOURCE_NAMES = ['CoreDictionaryUncased', 'CoreDictionaryExact', 'CancerLike',
                     'CommonSuffixes', 'Deficiency', 'Disorder',
                     'Lesion', 'Syndrome', 'BodyTerms',
                     'OtherPOS', 'StopWords', 'Punctuation',
                     'PossessivePhrase', 'HyphenatedPhrase', 'ElmoLinkingRule',
                     'CommonBigram', 'ExtractedPhrase']

NCBI_SOURCES_TO_KEEP = ['CoreDictionaryUncased', 'CoreDictionaryExact', 'CancerLike', 'BodyTerms', 'ExtractedPhrase']
# NCBI_SOURCES_TO_KEEP = ['CoreDictionaryUncased', 'CoreDictionaryExact']

NCBI_SOURCE_PRIORS = {
    'CoreDictionaryUncased': {lbs: (0.8, 0.7) for lbs in NCBI_LABELS},
    'CoreDictionaryExact': {lbs: (0.9, 0.5) for lbs in NCBI_LABELS},
    'CancerLike': {lbs: (0.5, 0.4) for lbs in NCBI_LABELS},
    'CommonSuffixes': {'DISEASE': (0.1, 0.1)},
    'Deficiency': {'DISEASE': (0.1, 0.1)},
    'Disorder': {'DISEASE': (0.1, 0.1)},
    'Lesion': {'DISEASE': (0.1, 0.1)},
    'Syndrome': {'DISEASE': (0.1, 0.1)},
    "BodyTerms": {lbs: (0.5, 0.4) for lbs in NCBI_LABELS},
    "OtherPOS": {'DISEASE': (0.1, 0.1)},
    "StopWords": {'DISEASE': (0.1, 0.1)},
    "Punctuation": {'DISEASE': (0.1, 0.1)},
    "PossessivePhrase": {'DISEASE': (0.1, 0.1)},
    "HyphenatedPhrase": {'DISEASE': (0.1, 0.1)},
    'ElmoLinkingRule': {'DISEASE': (0.1, 0.1)},
    'CommonBigram': {'DISEASE': (0.1, 0.1)},
    'ExtractedPhrase': {'DISEASE': (0.9, 0.9)}
}

LAPTOP_LABELS = ['TERM']
LAPTOP_BIO = ["O"] + ["%s-%s" % (bi, label) for label in LAPTOP_LABELS for bi in "BI"]
LAPTOP_INDICES = {label: i for i, label in enumerate(LAPTOP_BIO)}

LAPTOP_SOURCE_NAMES = ['CoreDictionary', 'OtherTerms', 'ReplaceThe', 'iStuff',
                       'Feelings', 'ProblemWithThe', 'External', 'StopWords',
                       'Punctuation', 'Pronouns', 'NotFeatures', 'Adv',
                       'CompoundPhrase', 'ElmoLinkingRule', 'ExtractedPhrase', 'ConsecutiveCapitals']

LAPTOP_SOURCES_TO_KEEP = ['CoreDictionary', 'OtherTerms', 'iStuff', 'ExtractedPhrase', 'ConsecutiveCapitals']

LAPTOP_SOURCE_PRIORS = {
    'CoreDictionary': {lbs: (0.9, 0.7) for lbs in LAPTOP_LABELS},
    'OtherTerms': {lbs: (0.6, 0.5) for lbs in LAPTOP_LABELS},
    'ReplaceThe': {lbs: (0.1, 0.1) for lbs in LAPTOP_LABELS},
    'iStuff': {'TERM': (0.6, 0.4)},
    'Feelings': {'TERM': (0.1, 0.1)},
    'ProblemWithThe': {'TERM': (0.1, 0.1)},
    'External': {'TERM': (0.5, 0.4)},
    'StopWords': {'TERM': (0.1, 0.1)},
    "Punctuation": {lbs: (0.5, 0.4) for lbs in LAPTOP_LABELS},
    "Pronouns": {'TERM': (0.1, 0.1)},
    "NotFeatures": {'TERM': (0.1, 0.1)},
    "Adv": {'TERM': (0.1, 0.1)},
    "CompoundPhrase": {'TERM': (0.1, 0.1)},
    "ElmoLinkingRule": {'TERM': (0.6, 0.4)},
    'ExtractedPhrase': {'TERM': (0.9, 0.9)},
    'ConsecutiveCapitals': {'TERM': (0.7, 0.6)}
}

BC5CDR_LABELS = ['Chemical', 'Disease']
BC5CDR_BIO = ["O"] + ["%s-%s" % (bi, label) for label in BC5CDR_LABELS for bi in "BI"]
BC5CDR_INDICES = {label: i for i, label in enumerate(BC5CDR_BIO)}

BC5CDR_SOURCE_NAMES = [
    'DictCore-Chemical', 'DictCore-Chemical-Exact', 'DictCore-Disease', 'DictCore-Disease-Exact',
    'Element, Ion, or Isotope', 'Organic Chemical', 'Antibiotic', 'Disease or Syndrome',
    'BodyTerms', 'Acronyms', 'Damage', 'Disease',
    'Disorder', 'Lesion', 'Syndrome', 'ChemicalSuffixes',
    'CancerLike', 'DiseaseSuffixes', 'DiseasePrefixes', 'Induced',
    'Vitamin', 'Acid', 'OtherPOS', 'StopWords',
    'CommonOther', 'Punctuation', 'PossessivePhrase', 'HyphenatedPrefix',
    'PostHyphen', 'ExtractedPhrase'
]

BC5CDR_SOURCES_TO_KEEP = [
    'DictCore-Chemical', 'DictCore-Chemical-Exact', 'DictCore-Disease', 'DictCore-Disease-Exact',
    'Organic Chemical', 'Disease or Syndrome', 'PostHyphen', 'ExtractedPhrase'
]

BC5CDR_SOURCE_PRIORS = {
    'DictCore-Chemical': {'Chemical': (0.9, 0.9), 'Disease': (0.1, 0.1)},
    'DictCore-Chemical-Exact': {'Chemical': (0.9, 0.5), 'Disease': (0.1, 0.1)},
    'DictCore-Disease': {'Chemical': (0.1, 0.1), 'Disease': (0.9, 0.9)},
    'DictCore-Disease-Exact': {'Chemical': (0.1, 0.1), 'Disease': (0.9, 0.5)},
    'Element, Ion, or Isotope': {'Chemical': (0.9, 0.4), 'Disease': (0.1, 0.1)},
    'Organic Chemical': {'Chemical': (0.9, 0.9), 'Disease': (0.1, 0.1)},
    'Antibiotic': {'Chemical': (0.9, 0.4), 'Disease': (0.1, 0.1)},
    'Disease or Syndrome': {'Chemical': (0.1, 0.1), 'Disease': (0.9, 0.7)},
    'BodyTerms': {'Chemical': (0.1, 0.1), 'Disease': (0.7, 0.3)},
    'Acronyms': {'Chemical': (0.1, 0.1), 'Disease': (0.1, 0.1)},
    'Damage': {'Chemical': (0.1, 0.1), 'Disease': (0.1, 0.1)},
    'Disease': {'Chemical': (0.1, 0.1), 'Disease': (0.1, 0.1)},
    'Disorder': {'Chemical': (0.1, 0.1), 'Disease': (0.1, 0.1)},
    'Lesion': {'Chemical': (0.1, 0.1), 'Disease': (0.1, 0.1)},
    'Syndrome': {'Chemical': (0.1, 0.1), 'Disease': (0.1, 0.1)},
    'ChemicalSuffixes': {'Chemical': (0.1, 0.1), 'Disease': (0.1, 0.1)},
    'CancerLike': {'Chemical': (0.1, 0.1), 'Disease': (0.7, 0.3)},
    'DiseaseSuffixes': {'Chemical': (0.1, 0.1), 'Disease': (0.1, 0.1)},
    'DiseasePrefixes': {'Chemical': (0.1, 0.1), 'Disease': (0.1, 0.1)},
    'Induced': {'Chemical': (0.1, 0.1), 'Disease': (0.1, 0.1)},
    'Vitamin': {'Chemical': (0.9, 0.3), 'Disease': (0.1, 0.1)},
    'Acid': {'Chemical': (0.9, 0.3), 'Disease': (0.1, 0.1)},
    'OtherPOS': {'Chemical': (0.1, 0.1), 'Disease': (0.1, 0.1)},
    'StopWords': {'Chemical': (0.1, 0.1), 'Disease': (0.1, 0.1)},
    'CommonOther': {'Chemical': (0.1, 0.1), 'Disease': (0.1, 0.1)},
    'Punctuation': {'Chemical': (0.1, 0.1), 'Disease': (0.1, 0.1)},
    'PossessivePhrase': {'Chemical': (0.2, 0.2), 'Disease': (0.2, 0.2)},
    'HyphenatedPrefix': {'Chemical': (0.2, 0.2), 'Disease': (0.2, 0.2)},
    'PostHyphen': {'Chemical': (0.8, 0.3), 'Disease': (0.8, 0.3)},
    'ExtractedPhrase': {'Chemical': (0.8, 0.3), 'Disease': (0.8, 0.3)},
}



"""Class containing some generic entity names (in English)"""

# List of currency symbols and three-letter codes
CURRENCY_SYMBOLS = {"$", "¥", "£", "€", "kr", "₽", "R$", "₹", "Rp", "₪", "zł", "Rs", "₺", "RS"}

CURRENCY_CODES = {"USD", "EUR", "CNY", "JPY", "GBP", "NOK", "DKK", "CAD", "RUB", "MXN", "ARS", "BGN",
                  "BRL", "CHF", "CLP", "CZK", "INR", "IDR", "ILS", "IRR", "IQD", "KRW", "KZT", "NGN",
                  "QAR", "SEK", "SYP", "TRY", "UAH", "AED", "AUD", "COP", "MYR", "SGD", "NZD", "THB",
                  "HUF", "HKD", "ZAR", "PHP", "KES", "EGP", "PKR", "PLN", "XAU", "VND", "GBX"}

# sets of tokens used for the shallow patterns
MONTHS = {"January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November",
          "December"}
MONTHS_ABBRV = {"Jan.", "Feb.", "Mar.", "Apr.", "May.", "Jun.", "Jul.", "Aug.", "Sep.", "Sept.", "Oct.", "Nov.", "Dec."}
DAYS = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"}
DAYS_ABBRV = {"Mon.", "Tu.", "Tue.", "Tues.", "Wed.", "Th.", "Thu.", "Thur.", "Thurs.", "Fri.", "Sat.", "Sun."}
MAGNITUDES = {"million", "billion", "mln", "bln", "bn", "thousand", "m", "k", "b", "m.", "k.", "b.", "mln.", "bln.",
              "bn."}
UNITS = {"tons", "tonnes", "barrels", "m", "km", "miles", "kph", "mph", "kg", "°C", "dB", "ft", "gal", "gallons", "g",
         "kW", "s", "oz",
         "m2", "km2", "yards", "W", "kW", "kWh", "kWh/yr", "Gb", "MW", "kilometers", "meters", "liters", "litres", "g",
         "grams", "tons/yr",
         'pounds', 'cubits', 'degrees', 'ton', 'kilograms', 'inches', 'inch', 'megawatts', 'metres', 'feet', 'ounces',
         'watts', 'megabytes',
         'gigabytes', 'terabytes', 'hectares', 'centimeters', 'millimeters', "F", "Celsius"}
ORDINALS = ({"first, second, third", "fourth", "fifth", "sixth", "seventh"} |
            {"%i1st" % i for i in range(100)} | {"%i2nd" % i for i in range(100)} | {"%ith" % i for i in range(1000)})
ROMAN_NUMERALS = {'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'XIII', 'XIV', 'XV', 'XVI',
                  'XVII',
                  'XVIII', 'XIX', 'XX', 'XXI', 'XXII', 'XXIII', 'XXIV', 'XXV', 'XXVI', 'XXVII', 'XXVIII', 'XXIX', 'XXX'}

# Full list of country names
COUNTRIES = {'Afghanistan', 'Albania', 'Algeria', 'Andorra', 'Angola', 'Antigua', 'Argentina', 'Armenia', 'Australia',
             'Austria',
             'Azerbaijan', 'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados', 'Belarus', 'Belgium', 'Belize', 'Benin',
             'Bhutan',
             'Bolivia', 'Bosnia Herzegovina', 'Botswana', 'Brazil', 'Brunei', 'Bulgaria', 'Burkina', 'Burundi',
             'Cambodia', 'Cameroon',
             'Canada', 'Cape Verde', 'Central African Republic', 'Chad', 'Chile', 'China', 'Colombia', 'Comoros',
             'Congo', 'Costa Rica',
             'Croatia', 'Cuba', 'Cyprus', 'Czech Republic', 'Denmark', 'Djibouti', 'Dominica', 'Dominican Republic',
             'East Timor',
             'Ecuador', 'Egypt', 'El Salvador', 'Equatorial Guinea', 'Eritrea', 'Estonia', 'Ethiopia', 'Fiji',
             'Finland', 'France',
             'Gabon', 'Gambia', 'Georgia', 'Germany', 'Ghana', 'Greece', 'Grenada', 'Guatemala', 'Guinea',
             'Guinea-Bissau', 'Guyana',
             'Haiti', 'Honduras', 'Hungary', 'Iceland', 'India', 'Indonesia', 'Iran', 'Iraq', 'Ireland', 'Israel',
             'Italy', 'Ivory Coast',
             'Jamaica', 'Japan', 'Jordan', 'Kazakhstan', 'Kenya', 'Kiribati', 'Korea North', 'Korea South', 'Kosovo',
             'Kuwait', 'Kyrgyzstan',
             'Laos', 'Latvia', 'Lebanon', 'Lesotho', 'Liberia', 'Libya', 'Liechtenstein', 'Lithuania', 'Luxembourg',
             'Macedonia', 'Madagascar',
             'Malawi', 'Malaysia', 'Maldives', 'Mali', 'Malta', 'Marshall Islands', 'Mauritania', 'Mauritius', 'Mexico',
             'Micronesia',
             'Moldova', 'Monaco', 'Mongolia', 'Montenegro', 'Morocco', 'Mozambique', 'Myanmar', 'Namibia', 'Nauru',
             'Nepal', 'Netherlands',
             'New Zealand', 'Nicaragua', 'Niger', 'Nigeria', 'Norway', 'Oman', 'Pakistan', 'Palau', 'Panama',
             'Papua New Guinea',
             'Paraguay', 'Peru', 'Philippines', 'Poland', 'Portugal', 'Qatar', 'Romania', 'Russian Federation',
             'Rwanda', 'St Kitts & Nevis',
             'St Lucia', 'Saint Vincent & the Grenadines', 'Samoa', 'San Marino', 'Sao Tome & Principe', 'Saudi Arabia',
             'Senegal', 'Serbia',
             'Seychelles', 'Sierra Leone', 'Singapore', 'Slovakia', 'Slovenia', 'Solomon Islands', 'Somalia',
             'South Africa', 'South Sudan',
             'Spain', 'Sri Lanka', 'Sudan', 'Suriname', 'Swaziland', 'Sweden', 'Switzerland', 'Syria', 'Taiwan',
             'Tajikistan', 'Tanzania',
             'Thailand', 'Togo', 'Tonga', 'Trinidad & Tobago', 'Tunisia', 'Turkey', 'Turkmenistan', 'Tuvalu', 'Uganda',
             'Ukraine',
             'United Arab Emirates', 'United Kingdom', 'United States', 'Uruguay', 'Uzbekistan', 'Vanuatu',
             'Vatican City', 'Venezuela',
             'Vietnam', 'Yemen', 'Zambia', 'Zimbabwe', "USA", "UK", "Russia", "South Korea"}

# Natialities, religious and political groups
NORPS = {'Afghan', 'African', 'Albanian', 'Algerian', 'American', 'Andorran', 'Anglican', 'Angolan', 'Arab', 'Aramean',
         'Argentine', 'Armenian',
         'Asian', 'Australian', 'Austrian', 'Azerbaijani', 'Bahamian', 'Bahraini', 'Baklan', 'Bangladeshi', 'Batswana',
         'Belarusian', 'Belgian',
         'Belizean', 'Beninese', 'Bermudian', 'Bhutanese', 'Bolivian', 'Bosnian', 'Brazilian', 'British', 'Bruneian',
         'Buddhist',
         'Bulgarian', 'Burkinabe', 'Burmese', 'Burundian', 'Californian', 'Cambodian', 'Cameroonian', 'Canadian',
         'Cape Verdian', 'Catholic', 'Caymanian',
         'Central African', 'Central American', 'Chadian', 'Chilean', 'Chinese', 'Christian', 'Christian-Democrat',
         'Christian-Democratic',
         'Colombian', 'Communist', 'Comoran', 'Congolese', 'Conservative', 'Costa Rican', 'Croat', 'Cuban', 'Cypriot',
         'Czech', 'Dane', 'Danish',
         'Democrat', 'Democratic', 'Djibouti', 'Dominican', 'Dutch', 'East European', 'Ecuadorean', 'Egyptian',
         'Emirati', 'English', 'Equatoguinean',
         'Equatorial Guinean', 'Eritrean', 'Estonian', 'Ethiopian', 'Eurasian', 'European', 'Fijian', 'Filipino',
         'Finn', 'Finnish', 'French',
         'Gabonese', 'Gambian', 'Georgian', 'German', 'Germanic', 'Ghanaian', 'Greek', 'Greenlander', 'Grenadan',
         'Grenadian', 'Guadeloupean', 'Guatemalan',
         'Guinea-Bissauan', 'Guinean', 'Guyanese', 'Haitian', 'Hawaiian', 'Hindu', 'Hinduist', 'Hispanic', 'Honduran',
         'Hungarian', 'Icelander', 'Indian',
         'Indonesian', 'Iranian', 'Iraqi', 'Irish', 'Islamic', 'Islamist', 'Israeli', 'Israelite', 'Italian', 'Ivorian',
         'Jain', 'Jamaican', 'Japanese',
         'Jew', 'Jewish', 'Jordanian', 'Kazakhstani', 'Kenyan', 'Kirghiz', 'Korean', 'Kurd', 'Kurdish', 'Kuwaiti',
         'Kyrgyz', 'Labour', 'Latin',
         'Latin American', 'Latvian', 'Lebanese', 'Liberal', 'Liberian', 'Libyan', 'Liechtensteiner', 'Lithuanian',
         'Londoner', 'Luxembourger',
         'Macedonian', 'Malagasy', 'Malawian', 'Malaysian', 'Maldivan', 'Malian', 'Maltese', 'Manxman', 'Marshallese',
         'Martinican', 'Martiniquais',
         'Marxist', 'Mauritanian', 'Mauritian', 'Mexican', 'Micronesian', 'Moldovan', 'Mongolian', 'Montenegrin',
         'Montserratian', 'Moroccan',
         'Motswana', 'Mozambican', 'Muslim', 'Myanmarese', 'Namibian', 'Nationalist', 'Nazi', 'Nauruan', 'Nepalese',
         'Netherlander', 'New Yorker',
         'New Zealander', 'Nicaraguan', 'Nigerian', 'Nordic', 'North American', 'North Korean', 'Norwegian', 'Orthodox',
         'Pakistani', 'Palauan',
         'Palestinian', 'Panamanian', 'Papua New Guinean', 'Paraguayan', 'Parisian', 'Peruvian', 'Philistine', 'Pole',
         'Polish', 'Portuguese',
         'Protestant', 'Puerto Rican', 'Qatari', 'Republican', 'Roman', 'Romanian', 'Russian', 'Rwandan',
         'Saint Helenian', 'Saint Lucian',
         'Saint Vincentian', 'Salvadoran', 'Sammarinese', 'Samoan', 'San Marinese', 'Sao Tomean', 'Saudi',
         'Saudi Arabian', 'Scandinavian', 'Scottish',
         'Senegalese', 'Serb', 'Serbian', 'Shia', 'Shiite', 'Sierra Leonean', 'Sikh', 'Singaporean', 'Slovak',
         'Slovene', 'Social-Democrat', 'Socialist',
         'Somali', 'South African', 'South American', 'South Korean', 'Soviet', 'Spaniard', 'Spanish', 'Sri Lankan',
         'Sudanese', 'Sunni',
         'Surinamer', 'Swazi', 'Swede', 'Swedish', 'Swiss', 'Syrian', 'Taiwanese', 'Tajik', 'Tanzanian', 'Taoist',
         'Texan', 'Thai', 'Tibetan',
         'Tobagonian', 'Togolese', 'Tongan', 'Tunisian', 'Turk', 'Turkish', 'Turkmen(s)', 'Tuvaluan', 'Ugandan',
         'Ukrainian', 'Uruguayan', 'Uzbek',
         'Uzbekistani', 'Venezuelan', 'Vietnamese', 'Vincentian', 'Virgin Islander', 'Welsh', 'West European',
         'Western', 'Yemeni', 'Yemenite',
         'Yugoslav', 'Zambian', 'Zimbabwean', 'Zionist'}

# Facilities
FACILITIES = {"Palace", "Temple", "Gate", "Museum", "Bridge", "Road", "Airport", "Hospital", "School", "Tower",
              "Station", "Avenue",
              "Prison", "Building", "Plant", "Shopping Center", "Shopping Centre", "Mall", "Church", "Synagogue",
              "Mosque", "Harbor", "Harbour",
              "Rail", "Railway", "Metro", "Tram", "Highway", "Tunnel", 'House', 'Field', 'Hall', 'Place', 'Freeway',
              'Wall', 'Square', 'Park',
              'Hotel'}

# Legal documents
LEGAL = {"Law", "Agreement", "Act", 'Bill', "Constitution", "Directive", "Treaty", "Code", "Reform", "Convention",
         "Resolution", "Regulation",
         "Amendment", "Customs", "Protocol", "Charter"}

# event names
EVENTS = {"War", "Festival", "Show", "Massacre", "Battle", "Revolution", "Olympics", "Games", "Cup", "Week", "Day",
          "Year", "Series"}

# Names of languages
LANGUAGES = {'Afar', 'Abkhazian', 'Avestan', 'Afrikaans', 'Akan', 'Amharic', 'Aragonese', 'Arabic', 'Aramaic',
             'Assamese', 'Avaric', 'Aymara',
             'Azerbaijani', 'Bashkir', 'Belarusian', 'Bulgarian', 'Bambara', 'Bislama', 'Bengali', 'Tibetan', 'Breton',
             'Bosnian', 'Cantonese',
             'Catalan', 'Chechen', 'Chamorro', 'Corsican', 'Cree', 'Czech', 'Chuvash', 'Welsh', 'Danish', 'German',
             'Divehi', 'Dzongkha', 'Ewe',
             'Greek', 'English', 'Esperanto', 'Spanish', 'Castilian', 'Estonian', 'Basque', 'Persian', 'Fulah',
             'Filipino', 'Finnish', 'Fijian', 'Faroese',
             'French', 'Western Frisian', 'Irish', 'Gaelic', 'Galician', 'Guarani', 'Gujarati', 'Manx', 'Hausa',
             'Hebrew', 'Hindi', 'Hiri Motu',
             'Croatian', 'Haitian', 'Hungarian', 'Armenian', 'Herero', 'Indonesian', 'Igbo', 'Inupiaq', 'Ido',
             'Icelandic', 'Italian', 'Inuktitut',
             'Japanese', 'Javanese', 'Georgian', 'Kongo', 'Kikuyu', 'Kuanyama', 'Kazakh', 'Kalaallisut', 'Greenlandic',
             'Central Khmer', 'Kannada',
             'Korean', 'Kanuri', 'Kashmiri', 'Kurdish', 'Komi', 'Cornish', 'Kirghiz', 'Latin', 'Luxembourgish', 'Ganda',
             'Limburgish', 'Lingala', 'Lao',
             'Lithuanian', 'Luba-Katanga', 'Latvian', 'Malagasy', 'Marshallese', 'Maori', 'Macedonian', 'Malayalam',
             'Mongolian', 'Marathi', 'Malay',
             'Maltese', 'Burmese', 'Nauru', 'Bokmål', 'Norwegian', 'Ndebele', 'Nepali', 'Ndonga', 'Dutch', 'Flemish',
             'Nynorsk', 'Navajo', 'Chichewa',
             'Occitan', 'Ojibwa', 'Oromo', 'Oriya', 'Ossetian', 'Punjabi', 'Pali', 'Polish', 'Pashto', 'Portuguese',
             'Quechua', 'Romansh', 'Rundi',
             'Romanian', 'Russian', 'Kinyarwanda', 'Sanskrit', 'Sardinian', 'Sindhi', 'Sami', 'Sango', 'Sinhalese',
             'Slovak', 'Slovenian', 'Samoan',
             'Shona', 'Somali', 'Albanian', 'Serbian', 'Swati', 'Sotho', 'Sundanese', 'Swedish', 'Swahili', 'Tamil',
             'Telugu', 'Tajik', 'Thai',
             'Tigrinya', 'Turkmen', 'Taiwanese', 'Tagalog', 'Tswana', 'Tonga', 'Turkish', 'Tsonga', 'Tatar', 'Twi',
             'Tahitian', 'Uighur', 'Ukrainian',
             'Urdu', 'Uzbek', 'Venda', 'Vietnamese', 'Volapük', 'Walloon', 'Wolof', 'Xhosa', 'Yiddish', 'Yoruba',
             'Zhuang', 'Mandarin',
             'Mandarin Chinese', 'Chinese', 'Zulu'}

LEGAL_SUFFIXES = {
    'ltd',  # Limited ~13.000
    'llc',  # limited liability company (UK)
    'ltda',  # limitada (Brazil, Portugal)
    'inc',  # Incorporated ~9700
    'co ltd',  # Company Limited ~9200
    'corp',  # Corporation ~5200
    'sa',  # Spółka Akcyjna (Poland), Société Anonyme (France)  ~3200
    'plc',  # Public Limited Company (Great Britain) ~2100
    'ag',  # Aktiengesellschaft (Germany) ~1000
    'gmbh',  # Gesellschaft mit beschränkter Haftung  (Germany)
    'bhd',  # Berhad (Malaysia) ~900
    'jsc',  # Joint Stock Company (Russia) ~900
    'co',  # Corporation/Company ~900
    'ab',  # Aktiebolag (Sweden) ~800
    'ad',  # Akcionarsko Društvo (Serbia), Aktsionerno Drujestvo (Bulgaria) ~600
    'tbk',  # Terbuka (Indonesia) ~500
    'as',  # Anonim Şirket (Turkey), Aksjeselskap (Norway) ~500
    'pjsc',  # Public Joint Stock Company (Russia, Ukraine) ~400
    'spa',  # Società Per Azioni (Italy) ~300
    'nv',  # Naamloze vennootschap (Netherlands, Belgium) ~230
    'dd',  # Dioničko Društvo (Croatia) ~220
    'a s',  # a/s (Denmark), a.s (Slovakia) ~210
    'oao',  # Открытое акционерное общество (Russia) ~190
    'asa',  # Allmennaksjeselskap (Norway) ~160
    'ojsc',  # Open Joint Stock Company (Russia) ~160
    'lp',  # Limited Partnership (US) ~140
    'llp',  # limited liability partnership
    'oyj',  # julkinen osakeyhtiö (Finland) ~120
    'de cv',  # Capital Variable (Mexico) ~120
    'se',  # Societas Europaea (Germany) ~100
    'kk',  # kabushiki gaisha (Japan)
    'aps',  # Anpartsselskab (Denmark)
    'cv',  # commanditaire vennootschap (Netherlands)
    'sas',  # société par actions simplifiée (France)
    'sro',  # Spoločnosť s ručením obmedzeným (Slovakia)
    'oy',  # Osakeyhtiö (Finland)
    'kg',  # Kommanditgesellschaft (Germany)
    'bv',  # Besloten Vennootschap (Netherlands)
    'sarl',  # société à responsabilité limitée (France)
    'srl',  # Società a responsabilità limitata (Italy)
    'sl'  # Sociedad Limitada (Spain)
}
# Generic words that may appear in official company names but are sometimes skipped when mentioned in news articles (e.g. Nordea Bank -> Nordea)
GENERIC_TOKENS = {"International", "Group", "Solutions", "Technologies", "Management", "Association", "Associates",
                  "Partners",
                  "Systems", "Holdings", "Services", "Bank", "Fund", "Stiftung", "Company"}

# List of tokens that are typically lowercase even when they occur in capitalised segments (e.g. International Council of Shopping Centers)
LOWERCASED_TOKENS = {"'s", "-", "a", "an", "the", "at", "by", "for", "in", "of", "on", "to", "up", "and"}

# Prefixes to family names that are often in lowercase
NAME_PREFIXES = {"-", "von", "van", "de", "di", "le", "la", "het", "'t'", "dem", "der", "den", "d'", "ter"}

