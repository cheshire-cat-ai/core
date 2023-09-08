import mimetypes
from copy import deepcopy
from typing import Dict
from tempfile import NamedTemporaryFile
from fastapi import Body, Request, APIRouter, HTTPException, UploadFile, BackgroundTasks
from cat.log import log
from cat.mad_hatter.registry import registry_search_plugins
from urllib.parse import urlparse
import requests

router = APIRouter()


# GET plugins
@router.get("/")
async def get_available_plugins(
    request: Request,
    query: str = None,
    #author: str = None, to be activated in case of more granular search
    #tag: str = None, to be activated in case of more granular search
) -> Dict:
    """List available plugins"""

    # retrieve plugins from official repo
    registry_plugins = await registry_search_plugins(query)
    # index registry plugins by url
    registry_plugins_index = {}
    for p in registry_plugins:
        plugin_url = p["url"]
        registry_plugins_index[plugin_url] = p

    # get active plugins
    ccat = request.app.state.ccat
    active_plugins = ccat.mad_hatter.load_active_plugins_from_db()

    # list installed plugins' manifest
    installed_plugins = []
    for p in ccat.mad_hatter.plugins.values():
        
        # get manifest
        manifest = deepcopy(p.manifest) # we make a copy to avoid modifying the plugin obj
        manifest["active"] = p.id in active_plugins # pass along if plugin is active or not
        
        # filter by query
        plugin_text = [str(field) for field in manifest.values()]
        plugin_text = " ".join(plugin_text).lower()
        if (query is None) or (query.lower() in plugin_text):
            installed_plugins.append(manifest)

        # do not show already installed plugins among registry plugins
        registry_plugins_index.pop( manifest["plugin_url"], None )

    return {
        "filters": {
            "query": query,
            #"author": author, to be activated in case of more granular search
            #"tag": tag, to be activated in case of more granular search
        },
        "installed": installed_plugins,
        "registry": list(registry_plugins_index.values())
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
    plugin_archive_path = f"/tmp/{file.filename}"
    with open(plugin_archive_path, "wb+") as f:
        f.write(file.file.read())

    background_tasks.add_task(
        ccat.mad_hatter.install_plugin, plugin_archive_path
    )

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "info": "Plugin is being installed asynchronously"
    }


@router.post("/upload/registry")
async def install_plugin_from_registry(
    request: Request,
    background_tasks: BackgroundTasks,
    url_repo: Dict = Body(example={"url": "https://github.com/plugin-dev-account/plugin-repo"})
    ) -> Dict:
    """Install a new plugin from external repository"""
    
    # search for a release on Github
    path_url = str(urlparse(url_repo["url"]).path)
    url = "https://api.github.com/repos" +  path_url + "/releases"
    response = requests.get(url)
    if response.status_code != 200:
            raise HTTPException(
                status_code = 503,
                detail = { "error": "Github API not available" }
            )
            
    response = response.json()
    
    #Check if there are files for the latest release
    if len(response) != 0: 
        url_zip = response[0]["assets"][0]["browser_download_url"]
    else:
        # if not, than download the zip repo
        # TODO: extracted folder still contains branch name
        url_zip = url_repo["url"] + "/archive/master.zip"
        
    # Get plugin name
    arr = path_url.split("/")
    arr.reverse()
    plugin_name = arr[0] + ".zip"

    with requests.get(url_zip, stream=True) as response:
        if response.status_code != 200:
            raise HTTPException(
                status_code = 400,
                detail = { "error": "" }
            )
        
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
                "filename": file.name,
                "content_type": mimetypes.guess_type(plugin_name)[0],
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
    
    try:
        # toggle plugin
        ccat.mad_hatter.toggle_plugin(plugin_id)
        return {
            "info": f"Plugin {plugin_id} toggled"
        }
    except Exception as e:
        raise HTTPException(
            status_code = 500,
            detail = { "error": str(e)}
        ) 


@router.get("/{plugin_id}")
async def get_plugin_details(plugin_id: str, request: Request) -> Dict:
    """Returns information on a single plugin"""

    # access cat instance
    ccat = request.app.state.ccat
    
    if not ccat.mad_hatter.plugin_exists(plugin_id):
        raise HTTPException(
            status_code = 404,
            detail = { "error": "Plugin not found" }
        )

    active_plugins = ccat.mad_hatter.load_active_plugins_from_db()

    # get manifest and active True/False. We make a copy to avoid modifying the original obj
    plugin_info = deepcopy(ccat.mad_hatter.plugins[plugin_id].manifest)
    plugin_info["active"] = plugin_id in active_plugins

    return {
        "data": plugin_info
    }


@router.delete("/{plugin_id}")
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
        "deleted": plugin_id
    }


@router.get("/settings/")
async def get_plugins_settings(request: Request) -> Dict:
    """Returns the settings of all the plugins"""

    # access cat instance
    ccat = request.app.state.ccat

    settings = []

    # plugins are managed by the MadHatter class
    for plugin in ccat.mad_hatter.plugins.values():
        plugin_settings = plugin.load_settings()
        plugin_schema = plugin.get_settings_schema()
        if plugin_schema['properties'] == {}:
            plugin_schema = {}
        settings.append({
            "name": plugin.id,
            "value": plugin_settings,
            "schema": plugin_schema
        })

    return {
        "settings": settings,
    }


@router.get("/settings/{plugin_id}")
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
    settings = ccat.mad_hatter.plugins[plugin_id].load_settings()
    schema = ccat.mad_hatter.plugins[plugin_id].get_settings_schema()
    if schema['properties'] == {}:
        schema = {}

    return {
        "name": plugin_id,
        "value": settings,
        "schema": schema
    }


@router.put("/settings/{plugin_id}")
async def upsert_plugin_settings(
    request: Request,
    plugin_id: str,
    payload: Dict = Body(example={"setting_a": "some value", "setting_b": "another value"}),
) -> Dict:
    """Updates the settings of a specific plugin"""

    # access cat instance
    ccat = request.app.state.ccat

    if not ccat.mad_hatter.plugin_exists(plugin_id):
        raise HTTPException(
            status_code = 404,
            detail = { "error": "Plugin not found" }
        )
    
    final_settings = ccat.mad_hatter.plugins[plugin_id].save_settings(payload)

    return {
        "name": plugin_id,
        "value": final_settings
    }