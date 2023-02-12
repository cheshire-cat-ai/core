import time

from typing import Union

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

from langchain.vectorstores import Qdrant

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

import openai
openai.api_key = 'INSERT YOUR KEY HERE'

app = FastAPI()


def embed(text):
    
    embedding = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )

    return embedding["data"][0]["embedding"]


qdrant_c = QdrantClient(host="vector-memory", port=6333)
qdrant_c.recreate_collection(
    collection_name='utterances',
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
)

vector_memory = Qdrant(
    qdrant_c,
    'utterances',
    embedding_function=embed
)


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:80/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.get("/")
def home():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        message = await websocket.receive_text()
        vector_ids = vector_memory.add_texts(
            [message],
            [{
                'who' : 'user',
                'when': time.time(),
                'text': message, 
            }]
        )
        #data = embed(data)
        await websocket.send_text(f'\nReceived: {vector_ids}')

        episodes = vector_memory.similarity_search(message) # TODO: why embed twice?
        for episode in episodes:
            await websocket.send_text(episode.page_content)