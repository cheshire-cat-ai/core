from typing import List
from copy import deepcopy
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from cat import log
from cat.mad_hatter.registry import registry_search_plugins
from cat.mad_hatter.plugin_manifest import PluginManifest
from cat.auth import get_user, get_ccat

router = APIRouter(prefix="/registry")

@router.get("")
async def registry_get_plugins(
    search: str = None,
    _ = get_user(),
    ccat = get_ccat(),
    # author: str = None, to be activated in case of more granular search
    # tag: str = None, to be activated in case of more granular search
) -> List[PluginManifest]:
    """List available plugins from registry."""

    # retrieve plugins from official repo
    registry_plugins = await registry_search_plugins(search)
    # index registry plugins by url
    registry_plugins_index = {}
    for p in registry_plugins:
        registry_plugins_index[p.id] = p

    # get active plugins
    active_plugins = await ccat.mad_hatter.get_active_plugins()

    # list installed plugins' manifest
    installed_plugins = []
    for p in ccat.mad_hatter.plugins.values():
        # get manifest
        manifest: PluginManifest = deepcopy(
            p.manifest
        )  # we make a copy to avoid modifying the plugin obj
        manifest.local_info["active"] = p.id in active_plugins

        # do not show already installed plugins among registry plugins
        r = registry_plugins_index.pop(manifest.plugin_url, None)

        manifest.local_info["upgrade"] = None
        # filter by query
        plugin_text = manifest.model_dump_json()
        if (search is None) or (search.lower() in plugin_text):
            if r is not None:
                if r.version is not None and r.version != p.manifest.version:
                    manifest["upgrade"] = r["version"]
            installed_plugins.append(manifest)

    return installed_plugins + registry_plugins

class PluginRegistryUpload(BaseModel):
    url: str

@router.post("/install")
async def registry_install_plugin(
    payload: PluginRegistryUpload,
    _ = get_user(role="admin"),
    ccat = get_ccat(),
) -> PluginManifest:
    """Install a new plugin from registry"""

    try:
        plugin = await ccat.mad_hatter.install_plugin(payload.url)
    except Exception:
        log.error("Could not install plugin from registry")
        raise HTTPException(status_code=500, detail="Could not install plugin from registry")

    return plugin.manifest
