import os
import json

from cat import utils
from cat.auth.permissions import AuthPermission, AuthResource
from cat.auth.connection import HTTPAuth
from fastapi import Depends, APIRouter, HTTPException, Request
from cat.db import models
from cat.db import crud
from cat.env import get_env
from cat.looking_glass.cheshire_cat import CheshireCat
from cat.memory.vector_memory import VectorMemory

router = APIRouter()


@router.get("/")
def get_settings(
    search: str = "",
    stray=Depends(HTTPAuth(AuthResource.SETTINGS, AuthPermission.LIST)),
):
    """Get the entire list of settings available in the database"""

    settings = crud.get_settings(search=search)

    return {"settings": settings}


@router.post("/")
def create_setting(
    payload: models.SettingBody,
    stray=Depends(HTTPAuth(AuthResource.SETTINGS, AuthPermission.WRITE)),
):
    """Create a new setting in the database"""

    # complete the payload with setting_id and updated_at
    payload = models.Setting(**payload.model_dump())

    # save to DB
    new_setting = crud.create_setting(payload)

    return {"setting": new_setting}


@router.get("/{settingId}")
def get_setting(
    settingId: str, stray=Depends(HTTPAuth(AuthResource.SETTINGS, AuthPermission.READ))
):
    """Get the a specific setting from the database"""

    setting = crud.get_setting_by_id(settingId)
    if not setting:
        raise HTTPException(
            status_code=404,
            detail={
                "error": f"No setting with this id: {settingId}",
            },
        )
    return {"setting": setting}


@router.put("/{settingId}")
def update_setting(
    settingId: str,
    payload: models.SettingBody,
    stray=Depends(HTTPAuth(AuthResource.SETTINGS, AuthPermission.EDIT)),
):
    """Update a specific setting in the database if it exists"""

    # does the setting exist?
    setting = crud.get_setting_by_id(settingId)
    if not setting:
        raise HTTPException(
            status_code=404,
            detail={
                "error": f"No setting with this id: {settingId}",
            },
        )

    # complete the payload with setting_id and updated_at
    payload = models.Setting(**payload.model_dump())
    payload.setting_id = settingId  # force this to be the setting_id

    # save to DB
    updated_setting = crud.update_setting_by_id(payload)

    return {"setting": updated_setting}


@router.delete("/{settingId}")
def delete_setting(
    settingId: str,
    stray=Depends(HTTPAuth(AuthResource.SETTINGS, AuthPermission.DELETE)),
):
    """Delete a specific setting in the database"""

    # does the setting exist?
    setting = crud.get_setting_by_id(settingId)
    if not setting:
        raise HTTPException(
            status_code=404,
            detail={
                "error": f"No setting with this id: {settingId}",
            },
        )

    # delete
    crud.delete_setting_by_id(settingId)

    return {"deleted": settingId}


@router.post("/factory-reset")
def factory_reset(
    request: Request,
    stray=Depends(HTTPAuth(AuthResource.SETTINGS, AuthPermission.WRITE)),
):
    """Delete Cat's memory and metadata.json file (settings db).
    A 'soft restart' is performed recreating the Cat instance and the metadata.json file.
    Plugins are not affected but need to be switched on.
    """

    metadata_file = get_env("CCAT_METADATA_FILE")
    metadata_content = {}

    try:
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r') as file:
                metadata_content = json.load(file)

            os.remove(metadata_file)

        vector_memory: VectorMemory = stray.memory.vectors
        deleted_memories = utils.delete_collections(vector_memory)

        utils.singleton.instances.clear()
        request.app.state.strays.clear()

        request.app.state.ccat = CheshireCat()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": f"An unexpected error occurred during factory reset: {str(e)}",
            },
        )

    return {"deleted_metadata": metadata_content, "deleted_memories": deleted_memories}
