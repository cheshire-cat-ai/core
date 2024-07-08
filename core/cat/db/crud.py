from typing import Dict, List
from uuid import uuid4

from tinydb import Query

from cat.auth.permissions import get_full_permissions, get_base_permissions
from cat.auth.auth_utils import hash_password
from cat.db import models
from cat.db.database import get_db


def get_settings(search: str = "") -> List[Dict]:
    query = Query()
    settings = get_db().search(query.name.matches(search))
    # Workaround: do not expose users in the settings list
    settings = [s for s in settings if s["name"] != "users"]
    return settings


def get_settings_by_category(category: str) -> List[Dict]:
    query = Query()
    return get_db().search(query.category == category)


def create_setting(payload: models.Setting) -> Dict:
    # Missing fields (setting_id, updated_at) are filled automatically by pydantic
    get_db().insert(payload.model_dump())

    # retrieve the record we just created
    new_record = get_setting_by_id(payload.setting_id)

    return new_record


def get_setting_by_name(name: str) -> Dict:
    query = Query()
    result = get_db().search(query.name == name)
    if len(result) > 0:
        return result[0]
    else:
        return None


def get_setting_by_id(setting_id: str) -> Dict:
    query = Query()
    result = get_db().search(query.setting_id == setting_id)
    if len(result) > 0:
        return result[0]
    else:
        return None


def delete_setting_by_id(setting_id: str) -> None:
    query = Query()
    get_db().remove(query.setting_id == setting_id)


def delete_settings_by_category(category: str) -> None:
    query = Query()
    get_db().remove(query.category == category)


def update_setting_by_id(payload: models.Setting) -> Dict:
    query = Query()
    get_db().update(payload, query.setting_id == payload.setting_id)

    return get_setting_by_id(payload.setting_id)


def upsert_setting_by_name(payload: models.Setting) -> models.Setting:
    old_setting = get_setting_by_name(payload.name)

    if not old_setting:
        create_setting(payload)
    else:
        query = Query()
        get_db().update(payload, query.name == payload.name)

    return get_setting_by_name(payload.name)


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