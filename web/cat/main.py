import traceback
import os
import time
from pprint import pprint
import json

from typing import Union

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, File, UploadFile, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from cat.utils import log
from cat.rabbit_hole import ingest_file # TODO: should be moved inside the cat as a method?
from cat.looking_glass import CheshireCat


#       ^._.^ 
# 
#  loads Cat and plugins
ccat = CheshireCat(
    verbose = True,
)


### API endpoints
cheshire_cat_api = FastAPI()

### list of allowed CORS origins.
### This list allows any domain to make requests to the server, 
### including sending cookies and using any HTTP method and header. 
### Whilst this is useful in dev environments, it might be too permissive for production environments
### therefore, it might be a good idea to configure the allowed origins in a differnet configuration file
origins = ["*"]

### Configures the CORS middleware for the FastAPI app
cheshire_cat_api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# server status
@cheshire_cat_api.get("/") 
def home():
    return {
        'status': "We're all mad here, dear!"
    }


# main loop via websocket
@cheshire_cat_api.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await websocket.accept()

    try:

        while True:

            # message received from user
            user_message = await websocket.receive_text() # TODO: should be JSON with metadata

            # get reponse from the cat
            cat_message = ccat(user_message)

            # send output to user
            await websocket.send_json(cat_message)


    except Exception as e:#WebSocketDisconnect as e:

        log(e)
        traceback.print_exc()

        # send error to user
        await websocket.send_json({
            'error': True,
            'code': type(e).__name__,
        })


# TODO: should we receive files also via websocket?
@cheshire_cat_api.post("/rabbithole/") 
async def rabbithole_upload_endpoint(file: UploadFile, background_tasks: BackgroundTasks):

    log(file.content_type)

    # list of admitted MIME types
    admitted_mime_types = [
        'text/plain',
        'application/pdf'
    ]
    
    
    # check id MIME type of uploaded file is supported
    if file.content_type not in admitted_mime_types:
        return {
            'error': f'MIME type {file.content_type} not supported. Admitted types: {" - ".join(admitted_mime_types)}'
        }
    
    # upload file to long term memory, in the background
    background_tasks.add_task(ingest_file, file, ccat)
    
    # reply to client
    return {
        'filename': file.filename,
        'content-type': file.content_type,
        'info': 'File is being ingested asynchronously.'
    }
