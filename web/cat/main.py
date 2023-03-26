import traceback

from cat import setting
from fastapi import FastAPI, WebSocket, UploadFile, BackgroundTasks
from cat.utils import log
from cat.rabbit_hole import (  # TODO: should be moved inside the cat as a method?
    ingest_file,
)
from cat.looking_glass import CheshireCat
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

#       ^._.^
#
# loads Cat and plugins
cheshire_cat = CheshireCat()

# API endpoints
cheshire_cat_api = FastAPI()


# list of allowed CORS origins.
# This list allows any domain to make requests to the server,
# including sending cookies and using any HTTP method and header.
# Whilst this is useful in dev environments, it might be too permissive for production environments
# therefore, it might be a good idea to configure the allowed origins in a differnet configuration file
origins = ["*"]  # TODO: add CORS_ALLOWED_ORIGINS support from .env

# Configures the CORS middleware for the FastAPI app
cheshire_cat_api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add the setting router to the middleware stack.
cheshire_cat_api.include_router(setting.router, tags=["Settings"], prefix="/settings")


# main loop via websocket
@cheshire_cat_api.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            # message received from user
            user_message = (
                await websocket.receive_text()
            )  # TODO: should receive a JSON with metadata

            # get response from the cat
            cat_message = cheshire_cat(user_message)

            # send output to user
            await websocket.send_json(cat_message)

    except Exception as e:  # WebSocketDisconnect as e:
        log(e)
        traceback.print_exc()

        # send error to user
        await websocket.send_json(
            {
                "error": True,
                "code": type(e).__name__,
            }
        )


# server status
@cheshire_cat_api.get("/")
async def home():
    return {"status": "We're all mad here, dear!"}


# POST delete_memories
@cheshire_cat_api.delete("/delete_memories/")
async def delete_memories(memory_id: str):
    return {"error": "to be implemented"}


# POST read_memories
@cheshire_cat_api.post("/recall_memories/")
async def recall_memories_from_text(text: str):
    memories = cheshire_cat.recall_memories_from_text(
        text=text, collection="episodes", k=100
    )
    documents = cheshire_cat.recall_memories_from_text(
        text=text, collection="documents", k=100
    )

    memories = [dict(m[0]) | {"score": float(m[1])} for m in memories]
    documents = [dict(m[0]) | {"score": float(m[1])} for m in documents]

    return (
        {
            "memories": memories,
            "documents": documents,
        },
    )


# receive files via endpoint
# TODO: should we receive files also via websocket?
@cheshire_cat_api.post("/rabbithole/")
async def rabbithole_upload_endpoint(
    file: UploadFile, background_tasks: BackgroundTasks
):
    log(file.content_type)

    # list of admitted MIME types
    admitted_mime_types = ["text/plain", "application/pdf"]

    # check id MIME type of uploaded file is supported
    if file.content_type not in admitted_mime_types:
        return JSONResponse(
            status_code=422,
            content={
                "error": f'MIME type {file.content_type} not supported. Admitted types: {" - ".join(admitted_mime_types)}'
            },
        )

    # upload file to long term memory, in the background
    background_tasks.add_task(ingest_file, file, cheshire_cat)

    # reply to client
    return {
        "filename": file.filename,
        "content-type": file.content_type,
        "info": "File is being ingested asynchronously.",
    }


# error handling
@cheshire_cat_api.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"error": exc.errors()},
    )


# Configure openAPI schema for swagger and redoc
def custom_openapi():
    if cheshire_cat_api.openapi_schema:
        return cheshire_cat_api.openapi_schema
    openapi_schema = get_openapi(
        title="😸 Cheshire-Cat API",
        version="0.1 (beta)",
        # TODO: this description should be more descriptive about the APIs capabilities
        description="Customizable AI architecture",
        routes=cheshire_cat_api.routes,
    )
    # Image should be an url and it's mostly used for redoc
    openapi_schema["info"]["x-logo"] = {
        "url": "https://github.com/pieroit/cheshire-cat/blob/main/cheshire-cat.jpeg?raw=true"
    }
    # Defines preconfigured examples for swagger
    # This example set parameter of /settings/ get: 'limit' to 3, page to 2 and search to "XYZ"
    # openapi_schema["paths"]["/settings/"]["get"]["parameters"][0]["example"] = 3
    # openapi_schema["paths"]["/settings/"]["get"]["parameters"][0]["example"] = 2
    # openapi_schema["paths"]["/settings/"]["get"]["parameters"][2]["example"] = "XYZ"
    cheshire_cat_api.openapi_schema = openapi_schema
    return cheshire_cat_api.openapi_schema


cheshire_cat_api.openapi = custom_openapi
