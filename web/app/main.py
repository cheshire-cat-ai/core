import os
import time
from pprint import pprint

from typing import Union

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from langchain.vectorstores import Qdrant
from langchain.llms import OpenAI

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

import openai
if not 'OPENAI_KEY' in os.environ:
    raise Exception('Please create a ".env" file in root folder containing "OPENAI_KEY=<your-key>"')
openai.api_key = os.environ['OPENAI_KEY']

llm = OpenAI(
    model_name='text-davinci-003',
    openai_api_key=openai.api_key
)

# from .agentManager import AgentManager
# am = AgentManager.singleton(llm=llm)

def embed(text):
    
    embedding = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )

    return embedding["data"][0]["embedding"] 


qdrant_c = QdrantClient(host="vector-memory", port=6333)
main_collection_name = 'utterances'

try:
    main_collection = qdrant_c.get_collection(main_collection_name)
    print('@@@ Main collection status:')
    pprint(main_collection.dict())
except:
    print('@@@ Creating main collection', qdrant_c.get_collections())
    qdrant_c.recreate_collection(
        collection_name=main_collection_name,
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
    )

vector_memory = Qdrant(
    qdrant_c,
    main_collection_name,
    embedding_function=embed
)

#### API endpoints

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
            message = await websocket.receive_text()
            #print('@@@@', message)

            vector_ids = vector_memory.add_texts(
                [message],
                [{
                    'who' : 'user',
                    'when': time.time(),
                    'text': message, 
                }]
            )

            # REPLY
            content = llm(message)
            
            # WHY
            why = 'here you will read WHY the cat gave a certain response'
            print('@@@@', message)
            #episodes = vector_memory.similarity_search(message) # TODO: why embed twice?
            #print('@@@@', episodes)
            #for episode in episodes:
            #    print('@@@@@', episode)
            #    why += ' ' + episode.page_content + ' |'
            
            await websocket.send_json({
                'content': content,
                'why'    : why,
            })


    except WebSocketDisconnect:
        print('@@ close connection')
        #del qdrant_c