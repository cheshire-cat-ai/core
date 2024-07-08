from enum import Enum
from typing import Dict, List


from cat.utils import BaseModelDict

class AuthResource(str, Enum):
    STATUS = "STATUS"
    MEMORY = "MEMORY"
    CONVERSATION = "CONVERSATION"
    SETTINGS = "SETTINGS"
    LLM = "LLM"
    EMBEDDER = "EMBEDDER"
    AUTH_HANDLER = "AUTH_HANDLER"
    USERS = "USERS"
    UPLOAD = "UPLOAD"
    PLUGINS = "PLUGINS"
    STATIC = "STATIC"

class AuthPermission(str, Enum):
    WRITE = "WRITE"
    EDIT = "EDIT"
    LIST = "LIST"
    READ = "READ"
    DELETE = "DELETE"


def get_full_permissions() -> Dict[AuthResource, List[AuthPermission]]:
    """
    Returns all available resources and permissions.
    """
    perms = {}
    for res in AuthResource:
        perms[res.name] = [p.name for p in AuthPermission]
    return perms


def get_base_permissions() -> Dict[AuthResource, List[AuthPermission]]:
    """
    Returns the default permissions for new users (chat only!).
    """
    return {
        "STATUS": ["READ"],
        "MEMORY": ["READ", "LIST"],
        "CONVERSATION": ["WRITE", "EDIT", "LIST", "READ", "DELETE"],
        "STATIC": ["READ"],
    }


class AuthUserInfo(BaseModelDict):
    """
    Class to represent token content after the token has been decoded.
    Will be creted by AuthHandler(s) to standardize their output.
    Core will use this object to retrieve or create a StrayCat (session)
    """

    # TODOAUTH: id & username can be confused when is time to retrieve or create a StrayCat
    # (id should be used)
    id: str
    name: str

    # permissions
    permissions: Dict[AuthResource, List[AuthPermission]] = get_base_permissions()

    # only put in here what you are comfortable to pass plugins:
    # - profile data
    # - custom attributes
    # - roles
    extra: BaseModelDict = {}

