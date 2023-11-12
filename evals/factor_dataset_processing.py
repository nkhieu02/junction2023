import numpy as np
import pdfplumber
import argparse
import pandas as pd
import config
import spacy

NLP = spacy.load(config.SPACY_MODEL)

def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', '-f', type=str, help='Path to input file')
    parser.add_argument('--threshold', '-t', type=float, help=\
                        'Minimum proption of proper sentence in a page')
    args = parser.parse_args()
    return args.file, args.threshold


# Functions used for parsing the output of pdfplumber
# which is a list of dictionary
def sentences_tokenize( chars):
    texts = [char['text'] for char in chars]
    fontsizes = [round(char['size'], 2) for char in chars]
    is_bolds = [('bold' in char['fontname'].lower()) for char in chars]
    paragraphs = []
    paragraph_is_bolds = []
    current_paragraph = texts[0]
    current_font = fontsizes[0]
    is_bold = is_bolds[0]

    for i in range(1, len(fontsizes)):
        if fontsizes[i] == current_font and is_bolds[i] == is_bold:
            current_paragraph += texts[i]
        else:
            paragraphs.append(current_paragraph)
            paragraph_is_bolds.append(is_bold)
            current_font = fontsizes[i]
            current_paragraph = texts[i]
            is_bold = is_bolds[i]
    paragraphs.append(current_paragraph)
    paragraph_is_bolds.append(is_bold)
    sentences = []
    sentence_is_bolds = []
    for i, paragraph in enumerate(paragraphs):
        doc = NLP(paragraph)
        sentences_tokenize = list(doc.sents)
        sentences += sentences_tokenize
        sentence_is_bolds += [paragraph_is_bolds[i]] * len(sentences_tokenize)
    return sentences, sentence_is_bolds

# Function to select sentence with noun and verb and more than
# 10 words - Proper sentence.
def filter_sentence( sentence, is_bold):
    pos_tags =  [token.pos_ for token in sentence]       
    return ((not is_bold) and (len(sentence.text.strip().split(' ')) > 10)) \
           and ('NOUN' in pos_tags or\
                'VERB' in pos_tags)

# Select pages with the propotion of workable sentences more than
# threshold.
def filter_page( sentences, is_bolds, threshhold):
    selected_sentences = [filter_sentence(sentence, is_bold)
                          for sentence, is_bold in zip(sentences, is_bolds)]
    if sum(selected_sentences) < threshhold * len(sentences):
        return False, sentences, selected_sentences
    else:
        return True, sentences, selected_sentences

# Process the pdf, return all the sentences and a list 
# of Boolean.
def process_pdf( file, threshold):
    pdf = pdfplumber.open(file)
    pages = pdf.pages
    sentences_a = []
    selected_sentences_a = []
    for page in pages:
        chars = page.chars
        selected, sentences, selected_sentences = \
        filter_page(*sentences_tokenize(chars), threshold)
        if selected:
            sentences_a += sentences
            selected_sentences_a += selected_sentences
    selected_sentences_a = np.where(selected_sentences_a)[0]
    return sentences_a, selected_sentences_a


def heuristic(sentence):
    errors = set()
    ner_tags = [ent.label_ for ent in sentence.ents]
    c_error_tags = ['LOC', 'DATE', 'TIME']
    if any([tag in c_error_tags for tag in ner_tags]):
        errors.add('CIRCUMSTANCES')
    
    for token in sentence:
        if len(errors) == 5:
            break
        pos = token.pos_ 
        if pos == 'NOUN':
            errors.add('ENTITY')
        if pos == 'VERB':
            errors.add('PREDICATE')
        if pos == 'NOUN':
            errors.add('COREFERENCE')  
        if str(token).lower() in config.LINKING_WORDS:
            errors.add('LINK')     
    return errors


if __name__ == "__main__":
    file, threshold = parse()
    sentences, selected_sentences = process_pdf(config.BASE_EVAL_DIR + file + '.pdf', threshold)
    data = {'errors': [], 'indices': []}

    for i in selected_sentences:
        s = sentences[i]
        error = heuristic(s)
        for e in error:
            data['errors'].append(e)
            data['indices'].append(i)
    
    s_df = pd.Series([s.text.strip() for s in sentences])
    df = pd.DataFrame(data)
    
    dir1 = config.BASE_EVAL_DIR + 'src_' + file + '.pkl'
    dir2 = config.BASE_EVAL_DIR + file + '.pkl'
    s_df.to_pickle(dir1)
    df.to_pickle(dir2)

    
    
    
    