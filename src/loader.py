from langchain.schema import Document
from typing import List
import os
import requests
import fitz
from dataclasses import dataclass
from dotenv import load_dotenv
from abc import ABC, abstractmethod
import requests

load_dotenv()

@dataclass
class BaseLoader(ABC):
    @abstractmethod
    def load(self, path) -> List[Document]:
        pass

@dataclass
class HtmlLoader(BaseLoader):
    '''
    Load text from an URL using EXTRACTOR_API
    '''
    endpoint: str = None
    api_token:str = None

    def __post_init__(self):
        self.endpoint = os.environ.get("EXTRACTOR_ENDPOINT")
        self.api_token = os.environ.get("EXTRACTOR_API_KEY")

    def load(self, path, metadata={}) -> List[Document]:
        params = {
        "apikey": self.api_token,
        "url": path,
        "fields": "domain,title,author,date_published",
        }
        response = requests.get(self.endpoint, params=params)
        if response.status_code == 200:            
            content = response.json()
            document = Document(page_content= content['text'], metadata=metadata)
            return [document]
        else:
            print(
                f"Hello person, there's a {response.status_code} error with your request")
            return None

@dataclass
class PdfLoader(BaseLoader):    
    
    def __post_init__(self):
        self.metadata = {'title': self.title, 'author': self.authors, 
                         'published': self.published, 'summary': self.summary}
        
    def load(self, path, metadata = {}) -> List[Document]:
        if not os.path.exists(path):
            local_path = f"../data/inference/{self.title}.pdf"
            if not os.path.exists(local_path):
                response = requests.get(path)
                with open(local_path, "wb") as f:
                    f.write(response.content)
                    f.flush()
        else:
            local_path = path
        with fitz.open(local_path) as doc_file:
            texts: str = "".join(page.get_text() for page in doc_file)
        
        return [Document(page_content=texts, metadata=metadata)]
    