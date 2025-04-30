from typing import Dict, List
from uuid import uuid4

from tinydb import Query

from cat.auth.permissions import get_full_permissions, get_base_permissions
from cat.auth.auth_utils import hash_password
from cat.db import models
from cat.db.database import get_db


def get_settings(search: str = "") -> List[Dict]:
    query = Query()

    settings = get_db().setting.query(query.name.matches(search), first=False)
    # Workaround: do not expose users in the settings list
    settings = [s for s in settings if s["name"] != "users"]
    return settings


def get_settings_by_category(category: str) -> List[Dict]:
    result = get_db().setting.get_by_attribute("category", category, first=False)
    if result:
        return result.model_dump(mode="json")
    return result

def create_setting(payload: models.Setting) -> Dict:
    result = get_db().setting.create(payload)
    if result:
        return result.model_dump(mode="json")
    return result

def get_setting_by_name(name: str) -> Dict:
    result = get_db().setting.get_by_attribute("name", name, first=True)
    if result:
        return result.model_dump(mode="json")
    return result

def get_setting_by_id(setting_id: str) -> Dict:
    result = get_db().setting.get_by_attribute("setting_id", setting_id, first=True)
    if result:
        return result.model_dump(mode="json")
    return result

def delete_setting_by_id(setting_id: str) -> None:
    result = get_db().setting.delete("setting_id", setting_id)
    if result:
        return result.model_dump(mode="json")
    return result

def delete_settings_by_category(category: str) -> None:
    result = get_db().setting.delete("category", category)
    if result:
        return result.model_dump(mode="json")
    return result

def update_setting_by_id(payload: models.Setting) -> Dict:
    result = get_db().setting.update(payload, "setting_id")
    if result:
        return result.model_dump(mode="json")
    return result

def upsert_setting_by_name(payload: models.Setting) -> models.Setting:
    result = get_db().setting.upsert(payload, "name")
    if result:
        return result.model_dump(mode="json")
    return result


# We store users in a setting and when there will be a graph db in the cat, we will store them there.
# P.S.: I'm not proud of this.
def get_users() -> Dict[str, Dict]:
    users = get_setting_by_name("users")
    if not users:
        # create admin user and an ordinary user
        admin_id = str(uuid4())
        user_id = str(uuid4())

        update_users({
            admin_id: {
                "id": admin_id,
                "username": "admin",
                "password": hash_password("admin"),
                # admin has all permissions
                "permissions": get_full_permissions()
            },
            user_id: {
                "id": user_id,
                "username": "user",
                "password": hash_password("user"),
                # user has minor permissions
                "permissions": get_base_permissions()
            }
        })
    return get_setting_by_name("users")["value"]

def update_users(users: Dict[str, Dict]) -> Dict[str, Dict]:
    updated_users = models.Setting(
        name="users",
        value=users
    )
    return upsert_setting_by_name(updated_users)