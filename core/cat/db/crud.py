
from typing import Dict, List
from tinydb import Query

from cat.db import models
from cat.db.database import Database
from cat.log import log


def get_settings(search: str = "") -> List[Dict]:
    query = Query()
    return Database().search(query.name.matches(search))


def get_settings_by_category(category: str) -> List[Dict]:
    query = Query()
    return Database().search(query.category == category)


def create_setting(payload: models.Setting) -> Dict:
    
    # Missing fields (setting_id, updated_at) are filled automatically by pydantic
    Database().insert(payload.dict())
    
    # retrieve the record we just created
    new_record = get_setting_by_id(payload.setting_id)

    return new_record 


def get_setting_by_name(name: str) -> Dict:
    query = Query()
    result = Database().search(query.name == name)
    if len(result) > 0:
        return result[0]
    else:
        return None 


def get_setting_by_id(setting_id: str) -> Dict:
    query = Query()
    result = Database().search(query.setting_id == setting_id)
    if len(result) > 0:
        return result[0]
    else:
        return None 


def delete_setting_by_id(setting_id: str) -> None:
    query = Query()
    Database().remove(query.setting_id == setting_id)    


def update_setting_by_id(payload: models.Setting) -> Dict:
    
    query = Query()
    Database().update(payload, query.setting_id == payload.setting_id)

    return get_setting_by_id(payload.setting_id)


def upsert_setting_by_name(payload: models.Setting) -> models.Setting:

    old_setting = get_setting_by_name(payload.name)

    if not old_setting:
        create_setting(payload)
    else:
        query = Query()
        Database().update(payload, query.name == payload.name)

    return get_setting_by_name(payload.name)