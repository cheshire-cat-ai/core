
from abc import ABC, abstractmethod

from cat.auth.utils import AuthPermission, AuthResource, AuthUserInfo
from fastapi import (
    WebSocket,
    Request,
    HTTPException
)
#from fastapi.security import OAuth2AuthorizationCodeBearer

from keycloak import KeycloakOpenID

from cat.env import get_env
from cat.log import log



class BaseAuthHandler(ABC): # TODOAUTH: pydantic model?
    """
    Base class to build custom Auth systems that will live alongside core auth.
    Methods `is_http_allowed` and `is_ws_allowed`
    MUST be implemented by subclasses.
    """

    @abstractmethod
    async def authorize_user_from_token(self, credential: str, auth_resource: AuthResource, auth_persmission: AuthPermission) -> AuthUserInfo | None:
        pass

    # TODOAUTH: all other abstract methods


# Default Auth, used for the legacy admin panel auth.
class NoAuthHandler(BaseAuthHandler):
    async def authorize_user_from_token(self, credential: str, auth_resource: AuthResource, auth_permission: AuthPermission) -> AuthUserInfo | None:       
        return AuthUserInfo(
            user_id="guest",
            user_data={}
        )
        
# Api Key Auth, require api_key usage
class ApiKeyAuthHandler(BaseAuthHandler):
    async def authorize_user_from_token(self, credential: str, auth_resource: AuthResource, auth_persmission: AuthPermission) -> AuthUserInfo | None:       
        environment_api_key = get_env("CCAT_API_KEY")
        if credential == environment_api_key:
            return AuthUserInfo(
                user_id="admin",
                user_data={}
            )
    
    
