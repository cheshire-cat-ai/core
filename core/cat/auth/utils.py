



from enum import Enum
from pydantic import BaseModel

AuthResource = Enum('AuthResource', ['STATUS', 'MEMORY', 'CONVERSATION', 'SETTINGS'])
AuthPermission = Enum('AuthPermission', ['WRITE', 'LIST', 'READ', 'DELETE'])

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

