import mimetypes
import os
from typing import Dict, Annotated
from tempfile import NamedTemporaryFile

from fastapi import Body, Request, APIRouter, HTTPException, UploadFile, BackgroundTasks
from cat.log import log
import httpx
import requests
from urllib.parse import urlparse

router = APIRouter()


# GET plugins
@router.get("/", status_code=200)
async def list_available_plugins(request: Request) -> Dict:
    """List available plugins"""

    # access cat instance
    ccat = request.app.state.ccat

    # plugins are managed by the MadHatter class
    plugins = []
    for p in ccat.mad_hatter.plugins.values():
        plugins.append(p.manifest)

    # retrieve plugins from official repo
    registry = [] #await get_registry_list()

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
            status_code = 400,
            detail={
                "error": f'MIME type `{file.content_type}` not supported. Admitted types: {", ".join(admitted_mime_types)}'
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
        "filename": file.filename,
        "content_type": file.content_type,
        "info": "Plugin is being installed asynchronously"
    }


@router.put("/toggle/{plugin_id}", status_code=200)
async def toggle_plugin(plugin_id: str, request: Request) -> Dict:
    """Enable or disable a single plugin"""

    # access cat instance
    ccat = request.app.state.ccat

    # check if plugin exists
    if not ccat.mad_hatter.plugin_exists(plugin_id):
        raise HTTPException(
            status_code = 404,
            detail = { "error": "Plugin not found" }
        )
    
    # toggle plugin
    ccat.mad_hatter.toggle_plugin(plugin_id)

    return {
        "status": "success",
        "info": f"Plugin {plugin_id} toggled"
    }


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

    plugin_info = ccat.mad_hatter.plugins[plugin_id].manifest

    return {
        "status": "success",
        "data": plugin_info
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
    
    # remove folder, hooks and tools
    ccat.mad_hatter.uninstall_plugin(plugin_id)

    return {
        "status": "success",
        "deleted": plugin_id
    }

async def get_registry_list():
    response = httpx.get("http://192.168.1.120:8000/plugins?page=1&page_size=7000")
    if response.status_code == 200:
        return response.json()["plugins"]
    else: 
        return []

@router.post("/upload/wa")
async def download_plugin_from_registry(request: Request,background_tasks: BackgroundTasks,url_repo: Dict = Body(example={"url": "https://example.com/file.zip"})):
    """Install a new plugin from external repository"""
    
    #Get name of file
    url_path = urlparse(url_repo["url"]).path.split("/")
    url_path.reverse()
    plugin_name = str(url_path[2]) + ".zip"
    
    
    with requests.get(url_repo["url"], stream=True) as response:
        response.raise_for_status()
        with NamedTemporaryFile(delete=False,mode="w+b",suffix=plugin_name) as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
            log(f"Uploading plugin {plugin_name}", "INFO")
            
            #access cat instance
            ccat = request.app.state.ccat

            background_tasks.add_task(
                ccat.mad_hatter.install_plugin, file.name
            )
            
            return {
                "status": "success",
                "filename": file.name,
                "content_type": mimetypes.guess_type(plugin_name)[0],
                "info": "Plugin is being installed asynchronously"
            }
    