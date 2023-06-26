import mimetypes
import tempfile
from typing import Dict
from zipfile import ZipFile
from fastapi import Request, APIRouter, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from cat.log import log


router = APIRouter()


# GET plugins
@router.get("/", status_code=200)
async def list_available_plugins(request: Request) -> Dict:
    """List available plugins"""

    # access cat instance
    ccat = request.app.state.ccat

    # plugins are managed by the MadHatter class a = b if b else val
    plugins = ccat.mad_hatter.plugins or []

    # retrieve plugins from official repo
    registry = []

    return {
        "status": "success", 
        "results": len(plugins) + len(registry), 
        "installed": plugins,
        "registry": registry
    }


@router.post("/upload/")
async def upload_plugin(
    request: Request,
    file: UploadFile
) -> Dict:
    """Install a new plugin from a zip file"""

    # access cat instance
    ccat = request.app.state.ccat

    # check if this is a zip file
    content_type = mimetypes.guess_type(file.filename)[0]
    log(f"Uploaded {content_type} plugin", "ERROR")
    if content_type != "application/zip":
        return JSONResponse(
            status_code=422,
            content={
                "error": f'MIME type `{file.content_type}` not supported. Please upload `application/zip` (a .zip file).'
            },
        )
    
    # Create temporary file (dunno how to extract from memory) #TODO: extract directly from memory
    file_bytes = file.file.read()
    temp_file = tempfile.NamedTemporaryFile(dir="/tmp/", delete=False)
    temp_name = temp_file.name
    with open(temp_name, "wb") as temp_binary_file:
        # Write bytes to file
        temp_binary_file.write(file_bytes)

    # Extracting into plugins folder
    with ZipFile(temp_name, 'r') as z_object:  
        z_object.extractall(path=ccat.get_plugin_path())

    # align plugins (may need to embed tools)
    ccat.bootstrap()

    # reply to client
    return {
        "filename": file.filename,
        "content-type": file.content_type,
        "info": "Plugin has been uploaded but not activated.",
    }


@router.put("/toggle/{plugin_id}", status_code=200)
async def toggle_plugin(plugin_id: str, request: Request) -> Dict:
    """Enable or disable a single plugin"""

    # access cat instance
    ccat = request.app.state.ccat

    return {"error": "to be implemented"}


@router.get("/{plugin_id}", status_code=200)
async def get_plugin_details(plugin_id: str, request: Request) -> Dict:
    """Returns information on a single plugin"""

    # access cat instance
    ccat = request.app.state.ccat

    # plugins are managed by the MadHatter class
    plugins = ccat.mad_hatter.plugins

    found = next(plugin for plugin in plugins if plugin["id"] == plugin_id)

    if not found:
        raise HTTPException(status_code=404, detail="Item not found")

    return {
        "status": "success", 
        "data": found
    }
