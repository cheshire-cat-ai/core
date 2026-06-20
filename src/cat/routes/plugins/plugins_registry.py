from typing import List
from copy import deepcopy
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from cat import log
from cat.mad_hatter.registry import registry_search_plugins
from cat.mad_hatter.plugin_manifest import PluginManifest
from cat.auth.depends import _get_user
from cat.ambient.runtime import ccat

router = APIRouter(prefix="/registry")

@router.get("")
async def registry_get_plugins(
    search: str = None,
    _ = _get_user(role="admin"),
    # author: str = None, to be activated in case of more granular search
    # tag: str = None, to be activated in case of more granular search
) -> List[PluginManifest]:
    """List available plugins from registry."""

    # retrieve plugins from official repo
    registry_plugins = await registry_search_plugins(search)
    # index registry plugins by their canonical home/repo URL — the natural join
    # key with installed plugins (both carry it as manifest.plugin_url). Local
    # identity is the folder name (Plugin.id); the registry download URL is
    # transport, not identity, so it is never used as an id here.
    registry_plugins_index = {p.plugin_url: p for p in registry_plugins}

    # get active plugins
    active_plugins = await ccat().mad_hatter.get_active_plugins()

    # list installed plugins' manifest
    installed_plugins = []
    for p in ccat().mad_hatter.plugins.values():
        # copy so we annotate the response, not the live plugin object
        manifest: PluginManifest = deepcopy(p.manifest)
        manifest.local_info["active"] = p.id in active_plugins

        # do not show already installed plugins among registry results
        r = registry_plugins_index.pop(manifest.plugin_url, None)

        manifest.local_info["upgrade"] = None
        if r is not None and r.version is not None and r.version != p.manifest.version:
            manifest.local_info["upgrade"] = r.version

        # filter by query
        plugin_text = manifest.model_dump_json()
        if (search is None) or (search.lower() in plugin_text):
            installed_plugins.append(manifest)

    # registry results minus the ones already installed (popped above)
    return installed_plugins + list(registry_plugins_index.values())

class PluginRegistryUpload(BaseModel):
    url: str

@router.post("/install")
async def registry_install_plugin(
    payload: PluginRegistryUpload,
    _ = _get_user(role="admin"),
) -> PluginManifest:
    """Install a new plugin from registry"""

    try:
        plugin = await ccat().mad_hatter.install_plugin(payload.url)
    except Exception:
        log.error("Could not install plugin from registry")
        raise HTTPException(status_code=500, detail="Could not install plugin from registry")

    return plugin.manifest
