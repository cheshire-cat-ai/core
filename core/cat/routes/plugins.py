from fastapi import Request, APIRouter, HTTPException, UploadFile, BackgroundTasks
from typing import Dict

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


@router.post("/install/")
async def install_plugin(
    request: Request,
    file: UploadFile,
    background_tasks: BackgroundTasks
) -> Dict:
    """Install a new plugin from a zip file"""

    # access cat instance
    ccat = request.app.state.ccat

    return {"error": "to be implemented"}


@router.put("/toggle/{plugin_id}", status_code=200)
async def toggle_plugin(plugin_id: str, request: Request) -> Dict:
    """Enable or disable a single plugin"""

    # access cat instance
    ccat = request.app.state.ccat

    return {"error": "to be implemented"}


@router.get("/{plugin_id}", status_code=200)
async def plugin_detail(plugin_id: str, request: Request) -> Dict:
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
