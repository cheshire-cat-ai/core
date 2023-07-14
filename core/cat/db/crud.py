
from typing import Dict
from tinydb import Query

from cat.db import models
from cat.db.database import Database
from cat.log import log


db = Database()


def get_settings(search: str = ""):
    query = Query()
    return (
        db.search(query.name.matches(search))
    )


def get_settings_by_category(category: str):
    query = Query()
    return db.search(query.category == category)


def create_setting(payload: models.Setting):
    #TODO before inserting we need to fill some field
    db.insert(payload.dict())
    db_setting = models.Setting(**payload.dict())
    return db_setting


def get_setting_by_name(name: str):
    query = Query()
    result = db.search(query.name == name)
    if len(result) > 0:
        return result[0]
    else:
        return None 


def get_setting_by_id(settingId: str):
    #TODO id is null by default
    return db.query(models.Setting).filter(models.Setting.setting_id == settingId)


def delete_setting_by_name(name: str) -> None:
    query = db.query(models.Setting).where(models.Setting.name == name)
    query.delete(synchronize_session=False)
    db.commit()

def upsert_setting(name: str, category: str, payload: Dict) -> models.Setting:

    old_setting = get_setting_by_name(db, name)

    if old_setting is None:
        # prepare setting to be included in DB, adding category
        setting = {
            "name": name,
            "value": payload,
            "category": category,
        }
        setting = models.Setting(**setting)
        final_setting = create_setting(db, setting).dict()
    
    else:
        old_setting.value = payload
        old_setting.updatedAt = func.now()
        db.add(old_setting)
        db.commit()
        db.refresh(old_setting)
        final_setting = old_setting.dict()

    return final_setting