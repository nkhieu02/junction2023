from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List
from langchain.schema import Document
from langchain.retrievers import BM25Retriever
from langchain.retrievers import TFIDFRetriever

@dataclass
class BaseRetriever(ABC):
    documents : List[Document]
    
    @abstractmethod
    def retrieve(self, query: str):
        pass
    
@dataclass
class Bm25Retriever(BaseRetriever):
    def retrieve(self, query: str):
        retriever = BM25Retriever.from_documents(self.documents)
        
        return retriever.get_relevant_documents(query)
    
@dataclass
class TfIdfRetrierver(BaseRetriever):
    def retrieve(self, query: str):
        retriever = TFIDFRetriever.from_documents(self.documents)
        
        return retriever.get_relevant_documents(query)
    