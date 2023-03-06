import os
import time
from pprint import pprint
import json

from typing import Union

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

import langchain
from langchain.llms import OpenAIChat
from langchain.embeddings import OpenAIEmbeddings

from langchain.cache import InMemoryCache # is it worth it to use a sqlite?
langchain.llm_cache = InMemoryCache()

import openai
if not 'OPENAI_KEY' in os.environ:
    raise Exception('Please create a ".env" file in root folder containing "OPENAI_KEY=<your-key>"')


from .utils import log
from .agent_manager import AgentManager
from .memory import get_vector_store


#### Large Language Model
# TODO: should be configurable via REST API
llm = OpenAIChat(
    model_name='gpt-3.5-turbo',
    openai_api_key=os.environ['OPENAI_KEY']
)


### Embedding LLM
# TODO: should be configurable via REST API
embedder = OpenAIEmbeddings(
    document_model_name='text-embedding-ada-002',
    openai_api_key=os.environ['OPENAI_KEY']
)


### Memory
episodic_memory    = get_vector_store('utterances', embedder=embedder)
declarative_memory = get_vector_store('documents', embedder=embedder)
# TODO: don't know if it is better to use different collections or just different metadata

### Agent
am = AgentManager.singleton(llm=llm)
agent_executor = am.get_agent_executor(['llm-math', 'python_repl'], return_intermediate_steps=True)


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

        history = ''
        memories_separator = '\n  -'

        while True:

            # message received from user
            user_message = await websocket.receive_text()
            
            # retrieve past memories
            episodic_memory_vectors = episodic_memory.max_marginal_relevance_search(user_message) # TODO: customize k and fetch_k
            episodic_memory_text = [m.page_content for m in episodic_memory_vectors]
            episodic_memory_content = memories_separator + memories_separator.join(episodic_memory_text) # TODO: take away duplicates; insert time information (e.g "two days ago")
            
            declarative_memory_content = '' # TODO: search in uploaded documents!
            
            # reply with agent
            cat_message = agent_executor({
                'input': user_message,
                'episodic_memory': episodic_memory_content,
                'declarative_memory': declarative_memory_content,
                'chat_history': history,
            })
            log(cat_message)
            
            # update conversation history
            history += f'Human: {user_message}\n'
            history += f'AI: {cat_message["output"]}\n'        
            
            # store user message in episodic memory
            # TODO: also embed HyDE style
            # TODO: vectorize and store conversation chunks
            vector_ids = episodic_memory.add_texts(
                [user_message],
                [{
                    #'who' : 'user', # TODO: is this necessary if there is a dedicated collection?
                    'when': time.time(),
                    'text': user_message, 
                }]
            )

            # build data structure for output (response and why with memories)
            final_output = {
                'content': cat_message['output'],
                'why'    : {
                    'intermediate_steps' : cat_message['intermediate_steps'],
                    'episodic_memory'    : episodic_memory_text,
                    'declarative_memory' : declarative_memory_content,
                },
            }

            # send output to user
            await websocket.send_json(final_output)


    except Exception as e:#WebSocketDisconnect as e:

        log(e)

        # send error to user
        await websocket.send_json({
            'content': 'Error: I just lost my head. Please refresh.',
            'why'    : {}, # TODO: pass error name? Danger zone
        })