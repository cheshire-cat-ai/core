from typing import Dict, List
from uuid import uuid4

from tinydb import Query

from cat.auth.permissions import get_full_permissions, get_base_permissions
from cat.auth.auth_utils import hash_password
from cat.db import models
from cat.db.database import get_db


def get_settings(search: str = "") -> List[Dict]:
    query = Query()

    settings = get_db().settings.query(query.name.matches(search), first=False)
    # Workaround: do not expose users in the settings list
    settings = [s for s in settings if s["name"] != "users"]
    return settings


def get_settings_by_category(category: str) -> List[Dict]:
    return get_db().settings.get_by_attribute("category", category, first=False)


def create_setting(payload: models.Setting) -> Dict:
    return get_db().settings.create(payload)


def get_setting_by_name(name: str) -> Dict:
    return get_db().settings.get_by_attribute("name", name, first=True)

def get_setting_by_id(setting_id: str) -> Dict:
    return get_db().settings.get_by_attribute("setting_id", setting_id, first=True)

def delete_setting_by_id(setting_id: str) -> None:
    return get_db().settings.delete("setting_id", setting_id)

def delete_settings_by_category(category: str) -> None:
    return get_db().settings.delete("category", category)


def update_setting_by_id(payload: models.Setting) -> Dict:
    return get_db().settings.update(payload, "setting_id")

def upsert_setting_by_name(payload: models.Setting) -> models.Setting:
    return get_db().settings.upsert(payload, "name")


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