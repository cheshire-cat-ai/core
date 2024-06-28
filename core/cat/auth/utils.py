from enum import Enum
from typing import Dict, List
from pydantic import BaseModel
import bcrypt
import jwt
from jwt.exceptions import InvalidTokenError

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
    ADMIN = "ADMIN"
    STATIC = "STATIC"

class AuthPermission(str, Enum):
    WRITE = "WRITE"
    EDIT = "EDIT"
    LIST = "LIST"
    READ = "READ"
    DELETE = "DELETE"


class AuthUserInfo(BaseModel):
    """
    Class to represent token content after the token has been decoded.
    Will be creted by AuthHandler(s) to standardize their output.
    Core will use this object to retrieve or create a StrayCat (session)
    """

    # user_id, used to retrieve or create a StrayCat
    user_id: str

    # only put in here what you are comfortable to pass plugins:
    # - profile data
    # - custom attributes
    # - roles
    # - permissions
    user_data: dict


def get_permissions_matrix() -> Dict[AuthResource, List[AuthPermission]]:
    """
    Returns all available resources and permissions.
    """
    perms = {}
    for res in AuthResource:
        perms[res.name] = [p.name for p in AuthPermission]
    return perms


def get_default_permissions() -> Dict[AuthResource, List[AuthPermission]]:
    """
    Returns the default permissions for new users (chat only!).
    """
    perms = {
        AuthResource.CONVERSATION.name: [],
    }
    for p in AuthPermission:
        perms[AuthResource.CONVERSATION].append(p.name)
    return perms


def is_jwt(token: str) -> bool:
    """
    Returns whether a given string is a JWT.
    """
    try:
        # Decode the JWT without verification to check its structure
        jwt.decode(token, options={"verify_signature": False})
        return True
    except InvalidTokenError:
        return False
    
def hash_password(password: str) -> str:
    try:
        # Generate a salt
        salt = bcrypt.gensalt()
        # Hash the password
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    except Exception:
        # if you try something strange, you'll stay out
        return bcrypt.gensalt().decode("utf-8")

def check_password(password: str, hashed: str) -> bool:
    try:
        # Check if the password matches the hashed password
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False
