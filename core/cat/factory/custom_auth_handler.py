
from abc import ABC, abstractmethod

from cat.auth.utils import AuthPermission, AuthResource, AuthUserInfo, is_jwt
import jwt
from cat.env import get_env
from cat.log import log

class BaseAuthHandler(ABC): # TODOAUTH: pydantic model?
    """
    Base class to build custom Auth systems that will live alongside core auth.
    Methods `authorize_user_from_token`
    MUST be implemented by subclasses.
    """

    @abstractmethod
    async def authorize_user_from_token(self, credential: str, auth_resource: AuthResource, auth_persmission: AuthPermission) -> AuthUserInfo | None:
        pass

# Core auth handler, verify token on local idp
class CoreAuthHandler(BaseAuthHandler):
    async def authorize_user_from_token(self, credential: str, auth_resource: AuthResource, auth_permission: AuthPermission) -> AuthUserInfo | None:       
        # Access token check for legacy admin
        if not is_jwt(credential):
            environment_api_key = get_env("CCAT_API_KEY")
            if credential == environment_api_key:
                return AuthUserInfo(
                    user_id="admin",
                    user_data={}
                )

        try:
            # decode token
            payload = jwt.decode(
                credential,
                get_env("CCAT_JWT_SECRET"),
                algorithms=[get_env("CCAT_JWT_ALGORITHM")]
            )

            # TODOAUTH: verify token expiration

            # build a user info obj that core can understand
            return AuthUserInfo(
                user_id=payload["username"],
                user_data=payload # TODOAUTH: maybe not the whole payload?
            )
        except Exception as e:
            log.error("Could not decode JWT")

        # do not pass
        return None
    

# Default Auth, always deny auth by default (only core auth decides).
class CloseAuthHandler(BaseAuthHandler):
    async def authorize_user_from_token(self, credential: str, auth_resource: AuthResource, auth_permission: AuthPermission) -> AuthUserInfo | None:       
        return None
        
# Api Key Auth, require CCAT_API_KEY usage for admin permissions and CCAT_API_KEY_WS for chat only permission
class ApiKeyAuthHandler(BaseAuthHandler):
    async def authorize_user_from_token(self, credential: str, auth_resource: AuthResource, auth_persmission: AuthPermission) -> AuthUserInfo | None:       
        environment_api_key = get_env("CCAT_API_KEY")
        environment_public_api_key = get_env("CCAT_API_KEY_WS")

        if auth_resource == AuthResource.CONVERSATION and auth_persmission == AuthPermission.WRITE and credential == environment_public_api_key:
            return AuthUserInfo(
                user_id="user",
                user_data={}
            )
        if credential == environment_api_key:
            return AuthUserInfo(
                user_id="admin",
                user_data={}
            )
    
    
