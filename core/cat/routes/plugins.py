import mimetypes
from fastapi import Body, Request, APIRouter, HTTPException, UploadFile, BackgroundTasks
from cat.log import log
from typing import Dict
import shutil

from tempfile import NamedTemporaryFile

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
async def install_plugin(
        request: Request,
        file: UploadFile,
        background_tasks: BackgroundTasks
) -> Dict:
    """Install a new plugin from a zip file"""

    # access cat instance
    ccat = request.app.state.ccat

    admitted_mime_types = ["application/zip", 'application/x-tar']
    content_type = mimetypes.guess_type(file.filename)[0]
    if content_type not in admitted_mime_types:
        raise HTTPException(
            status_code = 422,
            detail={
                "error": f'MIME type `{file.content_type}` not supported. Please upload a file of type ' +
                    f'({", ".join([mime for mime in admitted_mime_types])}).'
            },
        )

    log(f"Uploading {content_type} plugin {file.filename}", "INFO")
    temp = NamedTemporaryFile(delete=False, suffix=file.filename)
    contents = file.file.read()
    with temp as f:
        f.write(contents)

    background_tasks.add_task(
        ccat.mad_hatter.install_plugin, temp.name
    )

    return {
        "status": "success",
        "info": "Plugin is being installed asynchronously.",
        "filename": file.filename
    }


@router.put("/toggle/{plugin_id}", status_code=200)
async def toggle_plugin(plugin_id: str, request: Request) -> Dict:
    """Enable or disable a single plugin"""

    # access cat instance
    ccat = request.app.state.ccat

    raise HTTPException(
        status_code = 422,
        detail = { "error": "to be implemented" }
    )


@router.get("/{plugin_id}", status_code=200)
async def get_plugin_details(plugin_id: str, request: Request) -> Dict:
    """Returns information on a single plugin"""

    # access cat instance
    ccat = request.app.state.ccat

    if not ccat.mad_hatter.plugin_exists(plugin_id):
        raise HTTPException(
            status_code = 404,
            detail = { "error": "Plugin not found" }
        )

    plugin_info = [plugin for plugin in ccat.mad_hatter.plugins if plugin["id"] == plugin_id]

    return {
        "status": "success",
        "data": plugin_info[0]
    }


@router.get("/settings/{plugin_id}", status_code=200)
async def get_plugin_settings(request: Request, plugin_id: str) -> Dict:
    """Returns the settings of a specific plugin"""

    # access cat instance
    ccat = request.app.state.ccat

    if not ccat.mad_hatter.plugin_exists(plugin_id):
        raise HTTPException(
            status_code = 404,
            detail = { "error": "Plugin not found" }
        )

    # plugins are managed by the MadHatter class
    settings = ccat.mad_hatter.get_plugin_settings(plugin_id)

    return {
        "status": "success",
        "settings": settings,
        "schema": {}
    }


@router.put("/settings/{plugin_id}", status_code=200)
async def upsert_plugin_settings(
    request: Request,
    plugin_id: str,
    payload: Dict = Body(example={"active": False}),
) -> Dict:
    """Updates the settings of a specific plugin"""

    # access cat instance
    ccat = request.app.state.ccat

    if not ccat.mad_hatter.plugin_exists(plugin_id):
        raise HTTPException(
            status_code = 404,
            detail = { "error": "Plugin not found" }
        )
    
    final_settings = ccat.mad_hatter.save_plugin_settings(plugin_id, payload)

    return {
        "status": "success", 
        "settings": final_settings
    }


@router.delete("/{plugin_id}", status_code=200)
async def delete_plugin(plugin_id: str, request: Request) -> Dict:
    """Physically remove plugin."""

    # access cat instance
    ccat = request.app.state.ccat

    if not ccat.mad_hatter.plugin_exists(plugin_id):
        raise HTTPException(
            status_code = 404,
            detail = { "error": "Item not found" }
        )
    
    # remove plugin folder
    shutil.rmtree(ccat.get_plugin_path() + plugin_id)

    # align plugins (update db and embed new tools)
    ccat.bootstrap()

    return {
        "status": "success",
        "deleted": plugin_id
    }
