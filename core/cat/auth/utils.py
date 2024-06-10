



from enum import Enum
from pydantic import BaseModel
import jwt
from jwt.exceptions import InvalidTokenError

AuthResource = Enum('AuthResource', ['STATUS', 'MEMORY', 'CONVERSATION', 'SETTINGS', 'LLM', 'EMBEDDER', 'AUTH_HANDLER', 'UPLOAD', 'PLUGINS'])
AuthPermission = Enum('AuthPermission', ['WRITE', 'EDIT', 'LIST', 'READ', 'DELETE'])

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