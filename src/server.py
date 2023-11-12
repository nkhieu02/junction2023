import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import graph
from models import ChatOpenAI
import utils
app = FastAPI()

MESSAGES = [{
        "role": "system",
        "content": "My training data includes information up until January 2022. I'm here to provide the knowledge relating to three main context: \"business\", \"Findland\", and \"stainless steel\"."
}]
CHAT = ChatOpenAI(
        model='gpt-3.5-turbo'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
        return "Hello Junction 2023"

@app.post("/answer")
def create_answer(request : list[str]):
        global MESSAGES
        if len(request[0]) >= 1:
                MESSAGES.append({
                        "role": "assistant",
                        "content": request[0]
                })

        MESSAGES.append({
                "role": "user",
                "content": request[1]
        })
        tree = graph.Tot(utils.retrieve, utils.generate, utils.score, utils.goal_check, MESSAGES)
        thoughts = tree.search_answer()
        MESSAGES = thoughts
        MESSAGES.append({
                "role": "user",
                "content": "Now generate for me the last answer."
        })
        answer = CHAT.generate(input=MESSAGES, stream=True)
        result = [x.choices[0].delta.content for x in answer if x.choices[0].delta.content != None]
        return result

@app.post("/delete")
def delete_messages():
        global MESSAGES
        MESSAGES = [{
        "role": "system",
        "content": "My training data includes information up until January 2022. I'm here to provide the knowledge relating to three main context: \"business\", \"Findland\", and \"stainless steel\"."
        }]