import mimetypes
import requests
from typing import Dict
from fastapi import Body, Request, APIRouter, UploadFile, BackgroundTasks
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
        return JSONResponse(
            status_code=422,
            content={
                "error": f'MIME type {file.content_type} not supported. Admitted types: {" - ".join(admitted_mime_types)}'
            },
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
            return {"url": url, "info": "Invalid URL"}
    except requests.exceptions.RequestException as e:
        return {"url": url, "info": "Unable to reach the link"}


@router.post("/memory/")
async def upload_memory(
    request: Request,
    file: UploadFile,
    background_tasks: BackgroundTasks
) -> Dict:
    """Upload a memory json file to the cat memory"""

    # access cat instance
    ccat = request.app.state.ccat

    return {"error": "to be implemented"}
