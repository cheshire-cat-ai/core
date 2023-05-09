from cat.db import crud, models
from fastapi import Depends, Response, APIRouter, HTTPException, status
from sqlalchemy.orm import Session
from cat.db.database import get_db_session

router = APIRouter()


@router.get("/")
def get_settings(
    db: Session = Depends(get_db_session),
    limit: int = 100,
    page: int = 1,
    search: str = "",
):
    settings = crud.get_settings(db, limit=limit, page=page, search=search)

    return {"status": "success", "results": len(settings), "settings": settings}


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_setting(payload: models.Setting, db: Session = Depends(get_db_session)):
    new_setting = crud.create_setting(db, payload)
    return {"status": "success", "setting": new_setting}


@router.patch("/{settingId}")
def update_setting(
    settingId: str, payload: models.Setting, db: Session = Depends(get_db_session)
):
    setting_query = crud.get_setting_by_id(db, settingId=settingId)
    setting = setting_query.first()

    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No setting with this id: {settingId} found",
        )
    update_data = payload.dict(exclude_unset=True)
    setting_query.filter(models.Setting.setting_id == settingId).update(
        update_data, synchronize_session=False
    )
    db.commit()
    db.refresh(setting)
    return {"status": "success", "setting": setting}


@router.get("/{settingId}")
def get_setting(settingId: str, db: Session = Depends(get_db_session)):
    setting_query = crud.get_setting_by_id(db, settingId=settingId)
    setting = setting_query.first()
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No setting with this id: {id} found",
        )
    return {"status": "success", "setting": setting}


@router.delete("/{settingId}")
def delete_setting(settingId: str, db: Session = Depends(get_db_session)):
    setting_query = crud.get_setting_by_id(db, settingId=settingId)
    setting = setting_query.first()
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No setting with this id: {id} found",
        )
    setting_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
