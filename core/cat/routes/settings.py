from typing import Dict
from fastapi import APIRouter, HTTPException
from cat.db import models
from cat.db import crud

router = APIRouter()


@router.get("/")
def get_settings(search: str = "") -> Dict:
    """Get the entire list of settings available in the database"""

    settings = crud.get_settings(search=search)

    return {
        "settings": settings
    }


@router.post("/")
def create_setting(payload: models.SettingBody) -> Dict:
    """Create a new setting in the database"""

    # complete the payload with setting_id and updated_at
    payload = models.Setting(**payload.dict())

    # save to DB
    new_setting = crud.create_setting(payload)

    return {
        "setting": new_setting
    }


@router.get("/{settingId}")
def get_setting(settingId: str) -> Dict:
    """Get the a specific setting from the database"""

    setting = crud.get_setting_by_id(settingId)
    if not setting:
        raise HTTPException(
            status_code = 404,
            detail = {
                "error": f"No setting with this id: {settingId}",
            },
        )
    return {
        "setting": setting
    }


@router.put("/{settingId}")
def update_setting(settingId: str, payload: models.SettingBody) -> Dict:
    """Update a specific setting in the database if it exists"""

    # does the setting exist?
    setting = crud.get_setting_by_id(settingId)
    if not setting:
        raise HTTPException(
            status_code = 404,
            detail = {
                "error": f"No setting with this id: {settingId}",
            },
        )
    
    # complete the payload with setting_id and updated_at
    payload = models.Setting(**payload.model_dump())
    payload.setting_id = settingId # force this to be the setting_id

    # save to DB
    updated_setting = crud.update_setting_by_id(payload)
    
    return {
        "setting": updated_setting
    }


@router.delete("/{settingId}")
def delete_setting(settingId: str) -> Dict:
    """Delete a specific setting in the database"""

    # does the setting exist?
    setting = crud.get_setting_by_id(settingId)
    if not setting:
        raise HTTPException(
            status_code = 404,
            detail = {
                "error": f"No setting with this id: {settingId}",
            },
        )
    
    # delete
    crud.delete_setting_by_id(settingId)

    return {
        "deleted": settingId
    }
