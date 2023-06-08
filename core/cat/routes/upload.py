import mimetypes
from typing import Dict

from fastapi import Body, Request, APIRouter, UploadFile, BackgroundTasks
from cat.log import log
import requests
from fastapi.responses import JSONResponse

router = APIRouter()


# receive files via http endpoint
# TODO: should we receive files also via websocket?
@router.post("/")
async def rabbithole_upload_endpoint(
    request: Request,
    file: UploadFile,
    background_tasks: BackgroundTasks,
    chunk_size: int = Body(
        default=400,
        description="Maximum length of each chunk after the document is split (in characters)",
    ),
    chunk_overlap: int = Body(default=100, description="Chunk overlap (in characters)"),
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
        ccat.rabbit_hole.ingest_file, file, chunk_size, chunk_overlap
    )

    # reply to client
    return {
        "filename": file.filename,
        "content-type": file.content_type,
        "info": "File is being ingested asynchronously.",
    }


@router.post("/web/")
async def rabbithole_url_endpoint(
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
):
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
                ccat.rabbit_hole.ingest_url, url, chunk_size, chunk_overlap
            )
            return {"url": url, "info": "Website is being ingested asynchronously"}
        else:
            return {"url": url, "info": "Invalid URL"}
    except requests.exceptions.RequestException as e:
        return {"url": url, "info": "Unable to reach the link."}
