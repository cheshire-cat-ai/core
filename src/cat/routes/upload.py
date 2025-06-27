import mimetypes
import httpx
import io
import json
from typing import Dict, List
from copy import deepcopy

from pydantic import BaseModel, Field, ConfigDict

from fastapi import (
    Form,
    Request,
    APIRouter,
    UploadFile,
    BackgroundTasks,
    HTTPException,
)

from cat.auth.permissions import AuthPermission, AuthResource, check_permissions
from cat.log import log


# TODOV2:
# - add proper request and response pydantic models
# - cat.rabbit_hole without passing cat inside the function
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
    cat=check_permissions(AuthResource.UPLOAD, AuthPermission.WRITE),
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
    admitted_types = cat.rabbit_hole.file_handlers.keys()

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
        cat.rabbit_hole.ingest_file,
        cat,
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


# receive files via http endpoint
@router.post("/batch")
async def upload_files(
    request: Request,
    files: List[UploadFile],
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
        description="Metadata to be stored where each key is the name of a file being uploaded, and the corresponding value is another dictionary containing metadata specific to that file. "
                    "Since we are passing this along side form data, metadata must be a JSON string (use `json.dumps(metadata)`)."
    ),
    cat=check_permissions(AuthResource.UPLOAD, AuthPermission.WRITE),
) -> Dict:
    """Batch upload multiple files containing text (.txt, .md, .pdf, etc.). File content will be extracted and segmented into chunks.
    Chunks will be then vectorized and stored into documents memory.

    Note
    ----------
    `chunk_size`, `chunk_overlap` anad `metadata` must be passed as form data.
    This is necessary because the HTTP protocol does not allow file uploads to be sent as JSON.

    Example
    ----------
    ```
    files = []
    files_to_upload = {"sample.pdf":"application/pdf","sample.txt":"application/txt"}

    for file_name in files_to_upload:
        content_type = files_to_upload[file_name]
        file_path = f"tests/mocks/{file_name}"
        files.append(  ("files", ((file_name, open(file_path, "rb"), content_type))) )


    metadata = {
        "sample.pdf":{
            "source": "sample.pdf",
            "title": "Test title",
            "author": "Test author",
            "year": 2020
        },
        "sample.txt":{
            "source": "sample.txt",
            "title": "Test title",
            "author": "Test author",
            "year": 2021
        }
    }
        
    # upload file endpoint only accepts form-encoded data
    payload = {
        "chunk_size": 128,
        "metadata": json.dumps(metadata)
    }

    response = requests.post(
        "http://localhost:1865/rabbithole/batch",
        files=files,
        data=payload
    )
    ```
    """

    # Check the file format is supported
    admitted_types = cat.rabbit_hole.file_handlers.keys()
    log.info(f"Uploading {len(files)} files down the rabbit hole")

    response = {}
    metadata_dict = json.loads(metadata)

    for file in files:
        # Get file mime type
        content_type = mimetypes.guess_type(file.filename)[0]
        log.info(f"...Uploading {file.filename} {content_type}")

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
            cat.rabbit_hole.ingest_file,
            cat,
            deepcopy(format_upload_file(file)),
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            # if file.filename in dictionary pass the metadata otherwise pass empty dictionary 
            metadata=metadata_dict[file.filename] if file.filename in metadata_dict else {}
        )

        # reply to client
        response[file.filename] = {
            "filename": file.filename,
            "content_type": file.content_type,
            "info": "File is being ingested asynchronously",
        }

    return response

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
    cat=check_permissions(AuthResource.UPLOAD, AuthPermission.WRITE),
):
    """Upload a url. Website content will be extracted and segmented into chunks.
    Chunks will be then vectorized and stored into documents memory."""
    
    # check that URL is valid
    try:
        # Send a HEAD request to the specified URL
        async with httpx.AsyncClient() as client:
            response = await client.head(
                upload_config.url,
                headers={"User-Agent": "Magic Browser"},
                follow_redirects=True,
            )

        if response.status_code == 200:
            # upload file to long term memory, in the background
            background_tasks.add_task(
                cat.rabbit_hole.ingest_file,
                cat,
                upload_config.url,
                **upload_config.model_dump(exclude={"url"})
            )
            return {"url": upload_config.url, "info": "URL is being ingested asynchronously"}
        else:
            raise HTTPException(
                status_code=400,
                detail={"error": "Invalid URL", "url": upload_config.url},
            )
    except httpx.RequestError as _e:
        log.error(f"Unable to reach the URL {upload_config.url}")
        raise HTTPException(
            status_code=400,
            detail={"error": "Unable to reach the URL", "url": upload_config.url},
        )


@router.post("/memory")
async def upload_memory(
    request: Request,
    file: UploadFile,
    background_tasks: BackgroundTasks,
    cat=check_permissions(AuthResource.MEMORY, AuthPermission.WRITE),
) -> Dict:
    """Upload a memory json file to the cat memory"""

    # Get file mime type
    content_type = mimetypes.guess_type(file.filename)[0]
    log.info(f"Uploading {content_type} down the rabbit hole")
    if content_type != "application/json":
        raise HTTPException(
            status_code=400,
            detail={
                "error": f"MIME type {content_type} not supported. Admitted types: 'application/json'"
            },
        )

    # Ingest memories in background and notify client
    background_tasks.add_task(
        cat.rabbit_hole.ingest_memory,
        cat,
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
    cat=check_permissions(AuthResource.UPLOAD, AuthPermission.WRITE),
) -> Dict:
    """Retrieve the allowed mimetypes that can be ingested by the Rabbit Hole"""

    ccat = request.app.state.ccat

    admitted_types = list(ccat.rabbit_hole.file_handlers.keys())

    return {"allowed": admitted_types}
