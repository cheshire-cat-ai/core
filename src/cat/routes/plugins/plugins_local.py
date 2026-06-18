import aiofiles
import mimetypes
from typing import List
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, UploadFile
from cat import log
from cat.auth.depends import _get_user
from cat.context import app
from cat.mad_hatter.plugin_manifest import PluginManifest

router = APIRouter(prefix="/plugins")


class InstalledPlugin(BaseModel):
    id: str
    active: bool
    manifest: PluginManifest


@router.get("")
async def get_plugins(
    search: str = None,
    _ = _get_user(role="admin"),
) -> List[InstalledPlugin]:
    """List installed plugins"""

    ccat = app()
    # get active plugins
    active_plugins = await ccat.mad_hatter.get_active_plugins()

    # list installed plugins' manifest
    installed_plugins = []
    for p in ccat.mad_hatter.plugins.values():
        # filter by query
        plugin_text = p.manifest.model_dump_json()
        if (search is None) or (search.lower() in plugin_text):
            installed_plugins.append(
                InstalledPlugin(
                    id=p.id,
                    active=p.id in active_plugins,
                    manifest=p.manifest,
                )
            )

    return installed_plugins


@router.get("/{id}")
async def get_plugin(
    id: str,
    _ = _get_user(role="admin"),
) -> InstalledPlugin:
    """Returns information on a single plugin"""

    ccat = app()
    if not ccat.mad_hatter.plugin_exists(id):
        raise HTTPException(status_code=404, detail="Plugin not found")

    active_plugins = await ccat.mad_hatter.get_active_plugins()
    plugin = ccat.mad_hatter.plugins[id]

    return InstalledPlugin(
        id=plugin.id,
        active=plugin.id in active_plugins,
        manifest=plugin.manifest,
    )


@router.post("")
async def install_plugin(
    file: UploadFile,
    _ = _get_user(role="admin"),
) -> InstalledPlugin:
    """Install a new plugin from a zip file"""

    ccat = app()

    admitted_mime_types = [
        "application/zip", "application/x-tar"
    ]
    content_type = mimetypes.guess_type(file.filename)[0]
    if content_type not in admitted_mime_types:
        raise HTTPException(
            status_code=400,
            detail=(
                f'MIME type `{file.content_type}` not supported. '
                f'Admitted types: {", ".join(admitted_mime_types)}. '
            )
        )

    log.info(f"Uploading {content_type} plugin {file.filename}")
    plugin_archive_path = f"/tmp/{file.filename}"
    async with aiofiles.open(plugin_archive_path, "wb+") as f:
        content = await file.read()
        await f.write(content)

    plugin = await ccat.mad_hatter.install_plugin(plugin_archive_path)
    active_plugins = await ccat.mad_hatter.get_active_plugins()

    return InstalledPlugin(
        id=plugin.id,
        active=plugin.id in active_plugins,
        manifest=plugin.manifest
    )


@router.put("/{id}/toggle", status_code=200)
async def toggle_plugin(
    id: str,
    _ = _get_user(role="admin"),
):
    """Enable or disable a single plugin"""

    ccat = app()
    # check if plugin exists
    if not ccat.mad_hatter.plugin_exists(id):
        raise HTTPException(status_code=404, detail="Plugin not found")

    try:
        # toggle plugin
        await ccat.mad_hatter.toggle_plugin(id)
    except Exception as e:
        log.error(f"Could not toggle plugin {id}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{id}")
async def remove_plugin(
    id: str,
    _ = _get_user(role="admin"),
):
    """Physically remove plugin."""

    ccat = app()
    # check if plugin exists
    if not ccat.mad_hatter.plugin_exists(id):
        raise HTTPException(status_code=404, detail="Plugin not found")

    try:
        # remove folder, hooks and tools
        await ccat.mad_hatter.uninstall_plugin(id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
