
from abc import ABC, abstractmethod

from cat.auth.utils import AuthPermission, AuthResource, AuthUserInfo, is_jwt
import jwt
from cat.env import get_env
from cat.log import log

class BaseAuthHandler(ABC): # TODOAUTH: pydantic model?
    """
    Base class to build custom Auth systems that will live alongside core auth.
    Methods `authorize_user_from_credential`
    MUST be implemented by subclasses.
    """

    async def authorize_user_from_credential(
            self,
            credential: str,
            auth_resource: AuthResource,
            auth_permission: AuthPermission,
            # when there is no JWT, user id is passed via `user_id: xxx` header or via websocket path
            user_id: str = "user"
        ) -> AuthUserInfo | None:
        
        if is_jwt(credential):
            # JSON Web Token auth
            return await self.authorize_user_from_jwt(credential, auth_resource, auth_permission)
        else:
            # API_KEY auth
            return await self.authorize_user_from_key(user_id, credential, auth_resource, auth_permission)

    @abstractmethod
    async def authorize_user_from_jwt(
        self,
        token: str,
        auth_resource: AuthResource,
        auth_permission: AuthPermission
    ) -> AuthUserInfo | None:
        # will raise: NotImplementedError
        pass

    @abstractmethod
    async def authorize_user_from_key(
        self,
        user_id: str,
        api_key: str,
        auth_resource: AuthResource,
        auth_permission: AuthPermission
    ) -> AuthUserInfo | None:
        # will raise: NotImplementedError
        pass

# Core auth handler, verify token on local idp
class CoreAuthHandler(BaseAuthHandler):
    
    async def authorize_user_from_jwt(
        self,
        token: str,
        auth_resource: AuthResource,
        auth_permission: AuthPermission
    ) -> AuthUserInfo | None:
        
        try:
            # decode token
            payload = jwt.decode(
                token,
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
            log.error(f"Could not decode JWT: {e}")

        # do not pass
        return None
    
    async def authorize_user_from_key(
            self,
            user_id: str,
            api_key: str,
            auth_resource: AuthResource,
            auth_permission: AuthPermission,
        ) -> AuthUserInfo | None:       
        
        http_api_key = get_env("CCAT_API_KEY")
        ws_api_key = get_env("CCAT_API_KEY_WS")

        # chatting over websocket
        if auth_resource == AuthResource.CONVERSATION and api_key == ws_api_key:
            return AuthUserInfo(
                user_id=user_id,
                user_data={}
            )
        
        # any http endpoint
        if api_key == http_api_key:
            return AuthUserInfo(
                user_id=user_id,
                user_data={}
            )

        # do not pass
        return None
    

# Default Auth, always deny auth by default (only core auth decides).
class CoreOnlyAuthHandler(BaseAuthHandler):

    async def authorize_user_from_jwt(*args, **kwargs) -> AuthUserInfo | None:
        return None

    async def authorize_user_from_key(*args, **kwargs) -> AuthUserInfo | None:
        return None


# Api Key Auth, require CCAT_API_KEY usage for admin permissions and CCAT_API_KEY_WS for chat only permission
# TODOAUTH: review
class ApiKeyAuthHandler(BaseAuthHandler):
    async def authorize_user_from_token(self, credential: str, auth_resource: AuthResource, auth_permission: AuthPermission) -> AuthUserInfo | None:       
        environment_api_key = get_env("CCAT_API_KEY")
        environment_public_api_key = get_env("CCAT_API_KEY_WS")

        if auth_resource == AuthResource.CONVERSATION and auth_permission == AuthPermission.WRITE and credential == environment_public_api_key:
            return AuthUserInfo(
                user_id="user",
                user_data={}
            )
        if credential == environment_api_key:
            return AuthUserInfo(
                user_id="admin",
                user_data={}
            )
    
    
