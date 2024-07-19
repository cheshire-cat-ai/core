import mimetypes
import requests
import io
import json
from typing import Dict
from copy import deepcopy

from pydantic import BaseModel, Field, ConfigDict

from fastapi import (
    Form,
    Depends,
    Request,
    APIRouter,
    UploadFile,
    BackgroundTasks,
    HTTPException,
)

from cat.auth.connection import HTTPAuth
from cat.auth.permissions import AuthPermission, AuthResource
from cat.log import log


# TODOV2:
# - add proper request and response pydantic models
# - stray.rabbit_hole without passing cat inside the function
# - rabbit_hole methods should receive UploadConfig directly


router = APIRouter()


def format_upload_file(upload_file: UploadFile) -> UploadFile:
    file_content = upload_file.file.read()
    return UploadFile(filename=upload_file.filename, file=io.BytesIO(file_content))


# receive files via http endpoint
@router.post("/")
async def upload_file(
    request: Request,
    file: UploadFile,
    background_tasks: BackgroundTasks,
    chunk_size: int | None = Form(
        default=None,
        description="Maximum length of each chunk after the document is split (in tokens)"
    ),
    chunk_overlap: int | None = Form(
        default=None,
        description="Chunk overlap (in tokens)"
    ),
    metadata: str = Form(
        default="{}",
        description="Metadata to be stored with each chunk (e.g. author, category, etc.). "
                    "Since we are passing this along side form data, must be a JSON string (use `json.dumps(metadata)`)."
    ),
    stray=Depends(HTTPAuth(AuthResource.UPLOAD, AuthPermission.WRITE)),
) -> Dict:
    """Upload a file containing text (.txt, .md, .pdf, etc.). File content will be extracted and segmented into chunks.
    Chunks will be then vectorized and stored into documents memory.

    Note
    ----------
    `chunk_size`, `chunk_overlap` anad `metadata` must be passed as form data.
    This is necessary because the HTTP protocol does not allow file uploads to be sent as JSON.

    Example
    ----------
    ```
    content_type = "application/pdf"
    file_name = "sample.pdf"
    file_path = f"tests/mocks/{file_name}"
    with open(file_path, "rb") as f:
        files = {"file": (file_name, f, content_type)}

        metadata = {
            "source": "sample.pdf",
            "title": "Test title",
            "author": "Test author",
            "year": 2020,
        }
        # upload file endpoint only accepts form-encoded data
        payload = {
            "chunk_size": 128,
            "metadata": json.dumps(metadata)
        }

        response = requests.post(
            "http://localhost:1865/rabbithole/",
            files=files,
            data=payload
        )
    ```
    """

    # Check the file format is supported
    admitted_types = stray.rabbit_hole.file_handlers.keys()

    # Get file mime type
    content_type = mimetypes.guess_type(file.filename)[0]
    log.info(f"Uploaded {content_type} down the rabbit hole")

    # check if MIME type of uploaded file is supported
    if content_type not in admitted_types:
        raise HTTPException(
            status_code=400,
            detail={
                "error": f'MIME type {content_type} not supported. Admitted types: {" - ".join(admitted_types)}'
            },
        )

    # upload file to long term memory, in the background
    background_tasks.add_task(
        # we deepcopy the file because FastAPI does not keep the file in memory after the response returns to the client
        # https://github.com/tiangolo/fastapi/discussions/10936
        stray.rabbit_hole.ingest_file,
        stray,
        deepcopy(format_upload_file(file)),
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        metadata=json.loads(metadata)
    )

    # reply to client
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "info": "File is being ingested asynchronously",
    }

# This model can be used only for the upload_url endpoint,
# because in uplaod_file we need to pass the file and config as form data
class UploadURLConfig(BaseModel):
    url: str = Field(
        description="URL of the website to which you want to save the content"
    )
    chunk_size: int | None = Field(
        default=None,
        description="Maximum length of each chunk after the document is split (in tokens)"
    )
    chunk_overlap: int | None = Field(
        default=None,
        description="Chunk overlap (in tokens)"
    )
    metadata: Dict = Field(
        default={},
        description="Metadata to be stored with each chunk (e.g. author, category, etc.)"
    )
    model_config: ConfigDict = {"extra": "forbid"}

@router.post("/web")
async def upload_url(
    background_tasks: BackgroundTasks,
    upload_config: UploadURLConfig,
    stray=Depends(HTTPAuth(AuthResource.UPLOAD, AuthPermission.WRITE)),
):
    """Upload a url. Website content will be extracted and segmented into chunks.
    Chunks will be then vectorized and stored into documents memory."""
    
    # check that URL is valid
    try:
        # Send a HEAD request to the specified URL
        response = requests.head(
            upload_config.url, headers={"User-Agent": "Magic Browser"}, allow_redirects=True
        )

        if response.status_code == 200:
            # upload file to long term memory, in the background
            background_tasks.add_task(
                stray.rabbit_hole.ingest_file,
                stray,
                upload_config.url,
                **upload_config.model_dump(exclude={"url"})
            )
            return {"url": upload_config.url, "info": "URL is being ingested asynchronously"}
        else:
            raise HTTPException(
                status_code=400,
                detail={"error": "Invalid URL", "url": upload_config.url},
            )
    except requests.exceptions.RequestException as _e:
        raise HTTPException(
            status_code=400,
            detail={"error": "Unable to reach the URL", "url": upload_config.url},
        )


@router.post("/memory")
async def upload_memory(
    request: Request,
    file: UploadFile,
    background_tasks: BackgroundTasks,
    stray=Depends(HTTPAuth(AuthResource.MEMORY, AuthPermission.WRITE)),
) -> Dict:
    """Upload a memory json file to the cat memory"""

    # Get file mime type
    content_type = mimetypes.guess_type(file.filename)[0]
    log.info(f"Uploaded {content_type} down the rabbit hole")
    if content_type != "application/json":
        raise HTTPException(
            status_code=400,
            detail={
                "error": f"MIME type {content_type} not supported. Admitted types: 'application/json'"
            },
        )

    # Ingest memories in background and notify client
    background_tasks.add_task(
        stray.rabbit_hole.ingest_memory,
        stray,
        deepcopy(file)
    )

    # reply to client
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "info": "Memory is being ingested asynchronously",
    }


@router.get("/allowed-mimetypes")
async def get_allowed_mimetypes(
    request: Request,
    stray=Depends(HTTPAuth(AuthResource.UPLOAD, AuthPermission.WRITE)),
) -> Dict:
    """Retrieve the allowed mimetypes that can be ingested by the Rabbit Hole"""

    ccat = request.app.state.ccat

    admitted_types = list(ccat.rabbit_hole.file_handlers.keys())

    return {"allowed": admitted_types}
