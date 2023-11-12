from typing import Any, List, Optional, Iterable
from dataclasses import dataclass
from langchain.schema import Document
import copy
from config import SPACY_MODEL, LINKING_WORDS_DICT


LINKING_WORDS_SPLITTER = set()
for catgory in ['Alternatives', 'Analysing Results', 'Contrast', 'Emphasising', 'Examples', 'Re-phrasing']:
     LINKING_WORDS_SPLITTER.update(LINKING_WORDS_DICT[catgory])

     

def _make_spacy_pipeline_for_splitting(pipeline: str) -> Any:  # avoid importing spacy
    try:
        import spacy
    except ImportError:
        raise ImportError(
            "Spacy is not installed, please install it with `pip install spacy`."
        )
    if pipeline == "sentencizer":
        from spacy.lang.en import English

        sentencizer = English()
        sentencizer.add_pipe("sentencizer")
    else:
        sentencizer = spacy.load(pipeline, exclude=["ner", "tagger"])
    return sentencizer


@dataclass
class TextSplitter:

    length: int = 8
    sentence_tokenizer = _make_spacy_pipeline_for_splitting(SPACY_MODEL)
    
    def split_text(self, text: str) -> List[str]:
         '''
         If two sentences connected by linking words, should
         not be divided.
         '''
         sentences = self.sentence_tokenizer(text).sents
         docs = []
         count = 0
         current_doc = ''
         for s in sentences:
              index = min(len(s) , 5)
              if not any([word in s[0:index].text.lower() for word in LINKING_WORDS_SPLITTER]):
                  count += 1
                  if count <= self.length:
                      current_doc += s.text
                  else:
                      docs.append(current_doc)
                      current_doc = s.text
                      count = 1
              else:
                    current_doc += s.text
         return docs
                      
    def create_documents(
        self, texts: List[str], metadatas: Optional[List[dict]] = None
    ) -> List[Document]:
        """Create documents from a list of texts."""
        _metadatas = metadatas or [{}] * len(texts)
        documents = []
        for i, text in enumerate(texts):
            for j, chunk in enumerate(self.split_text(text)):
                metadata = copy.deepcopy(_metadatas[i])
                metadata['index'] = j
                new_doc = Document(page_content=chunk, metadata=metadata)
                documents.append(new_doc)
        return documents

    def split_documents(self, documents: Iterable[Document]) -> List[Document]:
        """Split documents."""
        texts, metadatas = [], []
        for doc in documents:
            texts.append(doc.page_content)
            metadatas.append(doc.metadata)
        return self.create_documents(texts, metadatas=metadatas)              
                   
