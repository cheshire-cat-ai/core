
from typing import Dict
from tinydb import Query

from cat.db import models
from cat.db.database import Database
from cat.log import log


db = Database()


def get_settings(search: str = ""):
    query = Query()
    return db.search(query.name.matches(search))


def get_settings_by_category(category: str):
    query = Query()
    return db.search(query.category == category)


def create_setting(payload: models.Setting) -> models.Setting:
    
    # Missing fields (setting_id, updated_at) are filled automatically by pydantic
    log(payload, "ERROR")
    log(payload.dict(), "ERROR")
    db.insert(payload.dict())
    
    # retrieve the record we just created
    new_record = get_setting_by_id(payload.setting_id)
    log(new_record, "WARNING")
    return new_record 


def get_setting_by_name(name: str) -> models.Setting:
    query = Query()
    result = db.search(query.name == name)
    if len(result) > 0:
        return result[0]
    else:
        return None 


def get_setting_by_id(setting_id: str) -> models.Setting:
    query = Query()
    result = db.search(query.setting_id == setting_id)
    if len(result) > 0:
        return result[0]
    else:
        return None 


def delete_setting_by_id(setting_id: str) -> None:
    query = Query()
    db.remove(query.setting_id == setting_id)    


def update_setting_by_id(payload: models.Setting) -> models.Setting:
    
    query = Query()
    db.update(payload, query.setting_id == payload.setting_id)

    return get_setting_by_id(payload.setting_id)


def upsert_setting_by_name(payload: models.Setting) -> models.Setting:

    old_setting = get_setting_by_name(payload.name)

    if not old_setting:
        create_setting(payload)
    else:
        query = Query()
        db.update(payload, query.name == payload.name)

    return get_setting_by_name(payload.name)