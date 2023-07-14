from fastapi import Depends, Response, APIRouter, HTTPException, status
from cat.db import models
from cat.db import crud


router = APIRouter()

@router.get("/")
def get_settings(search: str = ""):
    """Get the entire list of settings available in the database"""

    settings = crud.get_settings(search=search)

    return {
        "results": len(settings),
        "settings": settings
    }


@router.post("/")
def create_setting(payload: models.Setting):
    """Create a new setting in the database"""

    new_setting = crud.create_setting(payload)
    return {
        "status": "success",
        "setting": new_setting
    }


@router.put("/{settingId}")
def update_setting(settingId: str, payload: models.Setting):
    """Update a specific setting in the database"""

    setting_query = crud.get_setting_by_id(settingId=settingId)
    setting = setting_query.first()

    if not setting:
        raise HTTPException(
            status_code = 404,
            detail = {
                "error": f"No setting with this id: {settingId} found",
            },
        )
    update_data = payload.dict(exclude_unset=True)
    setting_query.filter(models.Setting.setting_id == settingId).update(
        update_data, synchronize_session=False
    )
    #db.commit()
    #db.refresh(setting)
    return {
        "status": "success",
        "setting": setting
    }


@router.get("/{settingId}")
def get_setting(settingId: str):
    """Get the a specific setting from the database"""

    setting_query = crud.get_setting_by_id(settingId=settingId)
    setting = setting_query.first()
    if not setting:
        raise HTTPException(
            status_code = 404,
            detail = {
                "error": f"No setting with this id: {id} found",
            },
        )
    return {
        "status": "success",
        "setting": setting
    }


@router.delete("/{settingId}")
def delete_setting(settingId: str):
    """Delete a specific setting in the database"""

    setting_query = crud.get_setting_by_id(settingId=settingId)
    setting = setting_query.first()
    if not setting:
        raise HTTPException(
            status_code = 404,
            detail = {
                "error": f"No setting with this id: {id} found",
            },
        )
    setting_query.delete(synchronize_session=False)
    #db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
