# Evaluate
import os
BASE_EVAL_DIR = os.path.join('..', 'data', 'eval')
SPACY_MODEL = 'en_core_web_md'
CONTEXT_SENTENCES = 50

# set of linking words
with open(os.path.join('..', 'resources', 'linking_words.txt'), 'r') as f:
    LINKING_WORDS =  set(f.read().lower().strip().split('\n'))