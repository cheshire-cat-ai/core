from cat.db import models
from sqlmodel import col
from sqlalchemy.orm import Session


def get_settings(db: Session, limit: int = 10, page: int = 1, search: str = ""):
    skip = (page - 1) * limit
    return (
        db.query(models.Setting)
        .where(col(models.Setting.name).contains(search))
        .limit(limit)
        .offset(skip)
        .all()
    )


def create_setting(db: Session, payload: models.Setting):
    db_setting = models.Setting(**payload.dict())
    db.add(db_setting)
    db.commit()
    db.refresh(db_setting)
    return db_setting


def get_setting_by_name(db: Session, name: str):
    return db.query(models.Setting).filter(models.Setting.name == name).first()


def get_setting_by_id(db: Session, settingId: str):
    return db.query(models.Setting).filter(models.Setting.setting_id == settingId)
