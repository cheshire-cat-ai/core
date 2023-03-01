import os
import time
from pprint import pprint
import json

from typing import Union

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

import langchain
from langchain.vectorstores import Qdrant
from langchain.llms import OpenAI
from langchain.embeddings import OpenAIEmbeddings

from langchain.cache import InMemoryCache # is it worth it to use a sqlite?
langchain.llm_cache = InMemoryCache()

import openai
if not 'OPENAI_KEY' in os.environ:
    raise Exception('Please create a ".env" file in root folder containing "OPENAI_KEY=<your-key>"')


from .utils import log
from .agent_manager import AgentManager

#### Large Language Model
llm = OpenAI(
    model_name='text-davinci-003',
    openai_api_key=os.environ['OPENAI_KEY']
)


### Embedding LLM
embedder = OpenAIEmbeddings(
    document_model_name='text-embedding-ada-002',
    openai_api_key=os.environ['OPENAI_KEY']
)


### Vector Memory
qd_client = QdrantClient(host="vector-memory", port=6333)
collection_name = 'utterances'

try:
    qd_client.get_collection(collection_name)
    log(f'Collection "{collection_name}" already present in vector store')
except:
    log(f'Creating collection {collection_name} ...')
    qd_client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE), # TODO: if we change the embedder, how do we know the dimensionality?
    )
    
log( dict(qd_client.get_collection(collection_name)) )

vector_memory = Qdrant(
    qd_client,
    collection_name,
    embedding_function=embedder.embed_query
)


### Agent
am = AgentManager.singleton(llm=llm)
agent = am.get_agent(['llm-math', 'python_repl'], return_intermediate_steps=True)


### API endpoints

app = FastAPI()


@app.get("/") 
def home():
    return {
        'status': 'ok'
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await websocket.accept()
    try:
        while True:
            
            # message received from user
            message = await websocket.receive_text()

            # retrieve past memories (should be done INSIDE agent)
            past_utterances_from_vector_memory = []
            utterances = vector_memory.max_marginal_relevance_search(message) # TODO: why embed twice?
            for utterance in utterances:
                past_utterances_from_vector_memory.append(utterance.page_content)

            # reply with agent
            response = agent({
                'input': message,
                'chat_history': '\n'.join(past_utterances_from_vector_memory) # TODO: this is not the way
            })
            
            
            # store user message in memory
            vector_ids = vector_memory.add_texts(
                [message],
                [{
                    'who' : 'user',
                    'when': time.time(),
                    'text': message, 
                }]
            )

            # send reply and why to user
            await websocket.send_json({
                'content': response['output'],
                'why'    : {
                    'intermediate_steps': response['intermediate_steps'],
                    'past_utterances_from_vector_memory' : past_utterances_from_vector_memory
                },
            })


    except WebSocketDisconnect:
        log('close connection')