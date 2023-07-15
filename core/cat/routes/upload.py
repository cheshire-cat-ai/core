import os
import json
import mimetypes
import tempfile
import requests
from typing import Dict
from qdrant_client.http import models
from fastapi import Body, Request, APIRouter, UploadFile, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse

from cat.log import log

router = APIRouter()


# receive files via http endpoint
# TODO: should we receive files also via websocket?
@router.post("/")
async def upload_file(
    request: Request,
    file: UploadFile,
    background_tasks: BackgroundTasks,
    chunk_size: int = Body(
        default=400,
        description="Maximum length of each chunk after the document is split (in characters)",
    ),
    chunk_overlap: int = Body(default=100, description="Chunk overlap (in characters)"),
    summary: bool = Body(default=False, description="Enables call to summary hook for this file")
) -> Dict:
    """Upload a file containing text (.txt, .md, .pdf, etc.). File content will be extracted and segmented into chunks.
    Chunks will be then vectorized and stored into documents memory.
    """

    ccat = request.app.state.ccat

    content_type = mimetypes.guess_type(file.filename)[0]
    log(f"Uploaded {content_type} down the rabbit hole", "INFO")
    # list of admitted MIME types

    admitted_mime_types = ["text/plain", "text/markdown", "application/pdf"]

    # check if MIME type of uploaded file is supported
    if content_type not in admitted_mime_types:
        raise HTTPException(
            status_code = 422,
            detail = { "error": f'MIME type {file.content_type} not supported. Admitted types: {" - ".join(admitted_mime_types)}' }
        )

    # upload file to long term memory, in the background
    background_tasks.add_task(
        ccat.rabbit_hole.ingest_file, file, chunk_size, chunk_overlap, summary
    )

    # reply to client
    return {
        "filename": file.filename,
        "content-type": file.content_type,
        "info": "File is being ingested asynchronously",
    }


@router.post("/web/")
async def upload_url(
    request: Request,
    background_tasks: BackgroundTasks,
    url: str = Body(
        description="URL of the website to which you want to save the content"
    ),
    chunk_size: int = Body(
        default=400,
        description="Maximum length of each chunk after the document is split (in characters)",
    ),
    chunk_overlap: int = Body(default=100, description="Chunk overlap (in characters)"),
    summary: bool = Body(default=False, description="Enables call to summary hook for this website")
):
    """Upload a url. Website content will be extracted and segmented into chunks.
    Chunks will be then vectorized and stored into documents memory."""
    # check that URL is valid
    try:
        # Send a HEAD request to the specified URL
        response = requests.head(url)
        status_code = response.status_code

        if status_code == 200:
            # Access the `ccat` object from the FastAPI application state
            ccat = request.app.state.ccat

            # upload file to long term memory, in the background
            background_tasks.add_task(
                ccat.rabbit_hole.ingest_url, url, chunk_size, chunk_overlap, summary
            )
            return {"url": url, "info": "Website is being ingested asynchronously"}
        else:
            raise HTTPException(
                status_code = 422,
                detail = {
                    "error": "Invalid URL",
                    "url": url
                },
            )
    except requests.exceptions.RequestException as _e:
        raise HTTPException(
            status_code = 422,
            detail = {
                "error": "Unable to reach the link",
                "url": url
            },
        )


@router.post("/memory/")
async def upload_memory(
    request: Request,
    file: UploadFile,
    background_tasks: BackgroundTasks
) -> Dict:
    """Upload a memory json file to the cat memory"""

    # access cat instance
    ccat = request.app.state.ccat

    # Check file mime type
    content_type = mimetypes.guess_type(file.filename)[0]

    # check if MIME type of uploaded file is supported
    if content_type != "application/json":
        raise HTTPException(
            status_code=422,
            detail={
                "error": f'MIME type {file.content_type} not supported. Admitted types: application/json'}
        )

    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(dir="/tmp/", delete=False)
    temp_name = temp_file.name

    # Get file bytes
    file_bytes = file.file.read()

    # Save in temporary file
    with open(temp_name, "wb") as temp_binary_file:
        temp_binary_file.write(file_bytes)

    # Recover the file as dict
    with open(temp_name, "r") as memories_file:
        memories = json.load(memories_file)

    # Check the embedder used for the uploaded memories is the same the Cat is using now
    upload_embedder = memories["embedder"]
    cat_embedder = str(ccat.embedder.__class__.__name__)

    if upload_embedder != cat_embedder:
        raise HTTPException(
            status_code=422,
            detail={
                "error": f'Embedder mismatch: uploaded file embedder {upload_embedder} is != from {ccat.embedder}'}
        )

    # Get Declarative memories in file
    declarative_memories = memories["collections"]["declarative"]

    # Store data to upload the memories with batch
    ids = [i["id"] for i in declarative_memories]
    payloads = [{
        "page_content": p["page_content"],
        "metadata": p["metadata"]
    } for p in declarative_memories]
    vectors = [v["vector"] for v in declarative_memories]

    # Check embedding size is correct
    embedder_size = ccat.memory.vectors.embedder_size
    len_mismatch = [len(v) == embedder_size for v in vectors]

    if not any(len_mismatch):
        raise HTTPException(
            status_code=422,
            detail={
                "error": f'Embedding size mismatch: vectors length should be {embedder_size}'}
        )

    # Upsert memories in batch mode
    ccat.memory.vectors.vector_db.upsert(
        collection_name="declarative",
        points=models.Batch(
            ids=ids,
            payloads=payloads,
            vectors=vectors
        )
    )

    # Remove temporary file
    os.remove(temp_name)

    # reply to client
    return {
        "error": False,
        "filename": file.filename,
        "content": f"Uploaded {len(ids)} memories in the Declarative memory"
    }
