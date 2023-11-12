import os
import json


SPACY_MODEL = 'en_core_web_md'
# linking words divided by most common use cases:
with open(os.path.join('..', 'resources', 'linking_words.json'), 'r') as f:
    LINKING_WORDS_DICT = json.load(f)

