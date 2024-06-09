
from abc import ABC, abstractmethod

from cat.auth.utils import AuthPermission, AuthResource, AuthUserInfo, is_jwt
import jwt
from fastapi import (
    WebSocket,
    Request,
)
from cat.env import get_env
from cat.log import log
from urllib.parse import parse_qs


class BaseAuthHandler(ABC): # TODOAUTH: pydantic model?
    """
    Base class to build custom Auth systems that will live alongside core auth.
    Methods `authorize_user_from_token`
    MUST be implemented by subclasses.
    """

    @abstractmethod
    async def authorize_user_from_token(self, credential: str, auth_resource: AuthResource, auth_persmission: AuthPermission) -> AuthUserInfo | None:
        pass

    async def http_extract_credential(self, request: Request) -> str | None:
        """
        Get JWT token or api key passed with the request
        """

        # Proper Authorization header
        authorization_header = request.headers.get("Authorization")
        if authorization_header and ("Bearer " in authorization_header):
            return authorization_header.replace("Bearer ", "")
            
        # Legacy header to pass CCAT_API_KEY
        access_token_header = request.headers.get("access_token")
        if access_token_header:
            log.warning(
                "Deprecation Warning: `access_token` header will not be supported in v2."
                "Pass your token/key using the `Authorization: Bearer <token>` format."
            )
            return access_token_header

        # no token found
        return None  

    async def ws_extract_credential(self, websocket: WebSocket) -> AuthUserInfo | None:
        """
        Extract token from WebSocket query string
        """
        query_params = parse_qs(websocket.url.query)
        return query_params.get("token", [None])[0]


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
    

# Default Auth, always deny auth by default.
class CloseAuthHandler(BaseAuthHandler):
    async def authorize_user_from_token(self, credential: str, auth_resource: AuthResource, auth_permission: AuthPermission) -> AuthUserInfo | None:       
        return None
        
# Api Key Auth, require CCAT_API_KEY usage for admin permissions and CCAT_PUBLIC_API_KEY for chat only permission
class ApiKeyAuthHandler(BaseAuthHandler):
    async def authorize_user_from_token(self, credential: str, auth_resource: AuthResource, auth_persmission: AuthPermission) -> AuthUserInfo | None:       
        environment_api_key = get_env("CCAT_API_KEY")
        environment_public_api_key = get_env("CCAT_PUBLIC_API_KEY")

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
    
    
