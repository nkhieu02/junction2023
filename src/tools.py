'''
Basically, business information can be divided into news,
case studies and research papers, and entities. So I aim to 
create 3 tools, one to search for the news (Fi and Eng), one
to search for academic paper using Arxiv.
'''

from serpapi import Client
from dotenv import load_dotenv
import os
from langchain.utilities.arxiv import ArxivAPIWrapper
load_dotenv()
from google.cloud import translate
from loader import HtmlLoader
from typing import List
from langchain.schema import Document
from splitter import TextSplitter
import logging
logger = logging.getLogger(__name__)

PROJECT_ID = os.environ.get("PROJECT_ID")
PARENT = f"projects/{PROJECT_ID}"

def translate_text(text: str, target_language_code: str) -> str:
    '''
    Requires some extra setting up.
    '''
    try:
        client = translate.TranslationServiceClient()
    
        response = client.translate_text(
            parent=PARENT,
            contents=[text],
            target_language_code=target_language_code,
        )
        return response.translations[0].translated_text

    except Exception as e:
        print('Setup unfinnished, no translation')
        return text
    
class ModifiedArxivWrapper(ArxivAPIWrapper):
    load_max_docs:int = 5
    def run(self, query: str) -> str:
        try:
            if self.is_arxiv_identifier(query):
                results = self.arxiv_search(
                    id_list=query.split(),
                    max_results=self.top_k_results,
                ).results()
            else:
                results = self.arxiv_search(  # type: ignore
                    query[: self.ARXIV_MAX_QUERY_LENGTH], max_results=self.top_k_results
                ).results()
        except self.arxiv_exceptions as ex:
            return f"Arxiv exception: {ex}"
        docs = [
            {"published": str(result.updated.date()),
            "title": result.title,
            "authors": [a.name for a in result.authors],
            "summary": result.summary,
            "link": [link.href for link in result.links]}
            for result in results
        ]
        if docs:
            return docs
        else:
            return "No good Arxiv Result was found"

    def load(self, query: str) -> List[Document]:
        """
        Run Arxiv search and get the article texts plus the article meta information.
        See https://lukasschwab.me/arxiv.py/index.html#Search

        Returns: a list of documents with the document.page_content in text format

        Performs an arxiv search, downloads the top k results as PDFs, loads
        them as Documents, and returns them in a List.

        Args:
            query: a plaintext search query
        """  # noqa: E501
        try:
            import fitz
        except ImportError:
            raise ImportError(
                "PyMuPDF package not found, please install it with "
                "`pip install pymupdf`"
            )

        try:
            # Remove the ":" and "-" from the query, as they can cause search problems
            query = query.replace(":", "").replace("-", "")
            if self.is_arxiv_identifier(query):
                results = self.arxiv_search(
                    id_list=query[: self.ARXIV_MAX_QUERY_LENGTH].split(),
                    max_results=self.load_max_docs,
                ).results()
            else:
                results = self.arxiv_search(  # type: ignore
                    query[: self.ARXIV_MAX_QUERY_LENGTH], max_results=self.load_max_docs
                ).results()
        except self.arxiv_exceptions as ex:
            logger.debug("Error on arxiv: %s", ex)
            return []

        docs: List[Document] = []
        for result in results:
            try:
                doc_file_name: str = result.download_pdf()
                with fitz.open(doc_file_name) as doc_file:
                    text: str = "".join(page.get_text() for page in doc_file)
            except (FileNotFoundError, fitz.fitz.FileDataError) as f_ex:
                logger.debug(f_ex)
                continue
            if self.load_all_available_meta:
                extra_metadata = {
                    "entry_id": result.entry_id,
                    "published_first_time": str(result.published.date()),
                    "comment": result.comment,
                    "journal_ref": result.journal_ref,
                    "doi": result.doi,
                    "primary_category": result.primary_category,
                    "categories": result.categories,
                    "links": [link.href for link in result.links],
                }
            else:
                extra_metadata = {}
            metadata = {
                "published": str(result.updated.date()),
                "title": result.title,
                "authors": ", ".join(a.name for a in result.authors),
                "summary": result.summary,
                **extra_metadata,
            }
            doc = Document(
                page_content=text[: self.doc_content_chars_max], metadata=metadata
            )
            docs.append(doc)
            os.remove(doc_file_name)
        return docs


client = Client(api_key=os.getenv('SERPAPI_API_KEY'))
arxiv_client = ModifiedArxivWrapper(
               top_k_results = 5,
               ARXIV_MAX_QUERY_LENGTH = 300,
               load_max_docs = 1,
               load_all_available_meta = False,
               doc_content_chars_max = 40000
               )
HTML_LOADER = HtmlLoader()
SPLITTER = TextSplitter()

fin_news_search_schema = \
{
 "type": "function",
 "function": {
     "name": "fin_news_search",
     "description": "Get current or past news in Finland",
     "parameters": {
         "type": "object",
         "properties": {
             "input": {
                 "type": "string",
                 "description": "Information to learn about"
             }
         },
         "required":["input"]
     }
    }
 }
def fin_news_search(input: str, domains = ['yle.fi', 'hs.fi', 'helsinkitimes.fi']):
    '''
    Output example
      "news_results": [
         {
             "position": 1,
             "link": "https://yle.fi/a/74-20057164",
             "title": "Health, trees, and beauty - the origins of the Finnish words for \"hello\"",
             "source": "Yle",
             "date": "2 weeks ago",
             "snippet": "Researchers at the University of Eastern Finland have researched the \norigins of the word \"moi\" and various other Finnish language greetings.",
             "thumbnail": "https://serpapi.com/searches/654fb9e6d5ecf46c3710a204/images/e0e3076b213825e3c71fd5bc5f18cb0eb3b4ea9719662b7a6ed5858aa90c82fe.jpeg"
         }
     ],
    '''
    # Try to  translate the input to Finnish:
    translated_input = input
    parameters = [{
        "engine": "google",
        "google_domain": "google.fi",
        "q": translated_input + ' ' + domain,
        "tbm": "nws",
        "num": 2

    } for domain in domains]
    raw_results = []
    documents = []
    for parameter in parameters:
        result = client.search(**parameter).get('news_results')
        if not result:
            continue
        raw_results += result
    print(raw_results)
    for result in raw_results:
        if not result:
            continue
        metadata = {}
        metadata['published'] = result.get('date')
        metadata['title'] = result.get('title')
        metadata['summary'] = result.get('snipper')
        metadata['link'] = result.get('link')
        document = HTML_LOADER.load(metadata['link'], metadata=metadata)
        documents += (document)
    documents = SPLITTER.split_documents(documents)
    return documents




news_search_schema = \
{
 "type": "function",
 "function": {
     "name": "news_search",
     "description": "Get current, up-to-date news around the world",
     "parameters": {
         "type": "object",
         "properties": {
             "input": {
                 "type": "string",
                 "description": "Information to learn about"
             },
             "domain": {
                 "type": "string",
                 "enum": ["hbr.com", "economist.com"],
                 "description": "hbr.com: general news, economist.com: general economic news"
             }
         },
         "required": ["input", "domain"]
     }
    }
 }
def news_search(input: str, domain: str):
    parameters = {
        "engine": "google",
        "google_domain": "google.fi",
        "q": input + ' ' + domain,
        "tbm": "nws",
        "num": 10
        } 
    raw_results = client.search(**parameters).get("news_results")
    documents = []
    if not raw_results:
        return documents
    for result in raw_results:
        if not result:
            continue
        metadata = {}
        metadata['published'] = result.get('date')
        metadata['title'] = result.get('title')
        metadata['summary'] = result.get('snipper')
        metadata['link'] = result.get('link')
        if not metadata['link']:
            continue
        document = HTML_LOADER.load(metadata['link'], metadata=metadata)
        documents += document
    documents = SPLITTER.split_documents(documents)
    return documents





entity_search_schema = \
{
 "type": "function",
 "function": {
     "name": "entity_search",
     "description": "Get general information about an entity",
     "parameters": {
         "type": "object",
         "properties": {
             "input": {
                 "type": "string",
                 "description": "Description or name of the entity"
             }
         }
     }
    }
 }
def entity_search(input: str):
    parameters = {
        "engine": "google",
        "google_domain": "google.fi",
        "q": input,
        }
    results = client.search(**parameters)
    return results.get('knowledge_graph')




academic_search_schema = \
{
 "type": "function",
 "function": {
     "name": "academics_search",
     "description": "Search Arxiv academics research, business case studies, ..",
     "parameters": {
         "type": "object",
         "properties": {
             "input": {
                 "type": "string",
                 "description": "Title of the papers, case studies,.."
             }
         },
         "required": ["input"]
     }
    }
 }
def academics_search(input: str):
    '''
    Output example:
    {"published": {result.updated.date()},
     "title": {result.title},
     "authors": {', '.join(a.name for a in result.authors)},
     "summary": {result.summary}}
    '''
    results = arxiv_client.load(query=input)
    results = SPLITTER.split_documents(results)
    return results

retrieve_schema = \
{
 "type": "function",
 "function": {
     "name": "retrieve",
     "description": "Retrieve local related documents",
     "parameters": {
         "type": "object",
         "properties": {
             "input": {
                 "type": "string",
                 "description": "Information you want to search"
             }
         },
         "required": ["input"]
     }
    }
 }

from retrievers import BaseRetriever
def retrieve(input: str, retriever: BaseRetriever = None):
    if retrieve == None:
        return []
    documents = retriever.retrieve(query=input)
    return documents


