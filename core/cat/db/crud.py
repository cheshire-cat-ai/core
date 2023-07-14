
from typing import Dict
from cat.db.database import Database
from tinydb import Query


def get_settings(db: Database, limit: int = 10, page: int = 1, search: str = ""):
    query = Query()
    return (
        db.search(query.name.matches(search))[:limit]
    )


def get_settings_by_category(db: Database, category: str):
    query = Query()
    return db.search(query.category == category)


def create_setting(db: Database, payload: models.Setting):
    #TODO before inserting we need to fill some field
    db.insert(payload.dict())
    db_setting = models.Setting(**payload.dict())
    return db_setting


def get_setting_by_name(db: Database, name: str):
    query = Query()
    return db.search(query.name == name)


def get_setting_by_id(db: Database, settingId: str):
    #TODO id is null by default
    return db.query(models.Setting).filter(models.Setting.setting_id == settingId)


def delete_setting_by_name(db: Database, name: str) -> None:
    query = db.query(models.Setting).where(models.Setting.name == name)
    query.delete(synchronize_session=False)
    db.commit()

def upsert_setting(db: Database,  name: str, category: str, payload: Dict) -> models.Setting:

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