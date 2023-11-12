import os
from dotenv import load_dotenv
from google.cloud import translate
from typing import Callable, List, Dict
from models import ChatOpenAI
import tools
from retrievers import BM25Retriever
from langchain.schema import Document
import re

def extract_float_from_string(input_string):
    # Define a regular expression pattern to match float values
    pattern = r'[-+]?\d*\.\d+|\d+'  # This pattern allows for positive/negative floats or integers

    # Use re.findall to find all matches of the pattern in the input string
    matches = re.findall(pattern, input_string)

    # If matches are found, return the first one as a float, otherwise return None
    return float(matches[0]) if matches else 5
import prompts

load_dotenv()
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

# FI_EN_MODEL = Huggingface_Model(model='Helsinki-NLP/opus-mt-fi-en')
# EN_FI_MODEL = Huggingface_Model(model='Helsinki-NLP/opus-mt-en-fi')

# def translate_fi_en(input: str) -> str:
#     result = FI_EN_MODEL.generate(input)
#     return result

# def translate_en_fi(input: str) -> str:
#     result = EN_FI_MODEL.generate(input)
#     return result

MODEL_NAME = 'gpt-3.5-turbo-1106'
MODEL = ChatOpenAI(model=MODEL_NAME)
TOOLS: Dict[str, Callable] = {
    'fin_news_search': tools.fin_news_search,
    'news_search': tools.news_search,
    'academic_seach': tools.academics_search,
    'retrieve': tools.retrieve
}
TOOLS_SCHEMAS = [tools.fin_news_search_schema, tools.news_search_schema, tools.academic_search_schema, tools.retrieve_schema]
RETRIEVER = BM25Retriever(docs=[])

def retrieve(messages: List[dict]):
    global RETRIEVER
    base_messages = messages
    prompt0 = "What are the missing contexts, informations to answer the previous questions?"
    base_messages.append({"role": "user", "content": prompt0})
    answer0 = MODEL.generate(base_messages, stream=False).choices[0].message.content
    base_messages.append({"role": "assistant", "content": answer0})
    prompt1 = 'Gather more information (if needed only). Generate why you need this information.'
    base_messages.append({'role': 'user', 'content': prompt1})
    function_responses = MODEL.function_calling(input=base_messages, tools=TOOLS,
                                                tool_schemas=TOOLS_SCHEMAS)
    length = len(function_responses)
    if length == 0:
        print('No function called')
    else:
        print('Function called')
        for r in function_responses:
            print(f'Input of the function {r["input"]}')
            print(f'Name of the function called {r["name"]}')
            if r["name"] != 'retrieve':
                RETRIEVER.docs += r["content"]



def generate(messages: List[dict], n: int) -> List[str]:
    global RETRIEVER
    thoughts = []

    function_responses = MODEL.function_calling(input=messages, tools=TOOLS,
                                                tool_schemas=TOOLS_SCHEMAS)
    documents = []
    for respon in function_responses:
        documents += respon["content"]
    prompt1 = f'Generate the next thought in {n} different ways, each way is separated by "|".'
    prompt2 = 'Here are informations related:\n'
    informations = '\n'.join([f'[{i}]:' + doc.page_content for i,doc in enumerate(documents)])
    generate_more_messages = messages +  [{'role': 'user', 'content': prompt2 + informations + '\n' + prompt1}]
    
    while len(thoughts) < n:
        answer = MODEL.generate(input=generate_more_messages, stream=False)
        results = answer.choices[0].message.content.split('|')
        i = min(len(results), n - len(thoughts))
        thoughts += results[0:i]
    return thoughts



def score(messages : List[dict]): 
    base_messages = messages
    promt = "Please mark the thought sequence above by a single digit number from 0 to 9 on how close it is to the final answer."
    base_messages.append({
        "role": "user",
        "content": promt
    })
    response = MODEL.generate(input=base_messages, stream=False).choices[0].message.content
    print(response)

    ### MISSING FUINCTION####
    score = extract_float_from_string(response)
    return score



def goal_check(messages: List[dict]) -> bool:
    base_messages = messages
    promt = "Please answer the question below with ONLY yes or no based on the provided conversation."
    promt = promt + "Are these thoughts enough to answer the user's question?"
    base_messages.append({
        "role": "user",
        "content": promt
    })
    response = MODEL.generate(input=messages, stream=False)
    if ("yes" in response.choices[0].message.content.lower()):
        return True
    else:
        return False


# generate: Callable[[List[str], str, int], List[str]]
# score: Callable[[List[str], str], float]
# goal_check: Callable[[List[str], str], bool]
