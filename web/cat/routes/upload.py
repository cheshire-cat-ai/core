from cat.utils import log

from fastapi import Body, Request, APIRouter, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse
import mimetypes

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
            description="Maximum length of each chunk after the document is split (in characters)"
        ),
        chunk_overlap: int = Body(
            default=100,
            description="Chunk overlap (in characters)"
        )
):
    """Upload a file containing text (.txt, .md, .pdf, etc.). File content will be extracted and segmented into chunks.
    Chunks will be then vectorized and stored into documents memory.
    """

    ccat = request.app.state.ccat

    content_type = mimetypes.guess_type(file.filename)[0]
    log(f"Uploaded {content_type} down the rabbit hole")
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
    background_tasks.add_task(ccat.send_file_in_rabbit_hole, file, chunk_size, chunk_overlap)

    # reply to client
    return {
        "filename": file.filename,
        "content-type": file.content_type,
        "info": "File is being ingested asynchronously.",
    }
