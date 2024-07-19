from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pytz import utc
import jwt

from cat.db.crud import get_users
from cat.auth.permissions import (
    AuthPermission, AuthResource, AuthUserInfo, get_base_permissions, get_full_permissions
)
from cat.auth.auth_utils import is_jwt, check_password
from cat.env import get_env
from cat.log import log


class BaseAuthHandler(ABC):  # TODOAUTH: pydantic model?
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
        # with JWT, the user id is in the token ad has priority
        user_id: str = "user",
    ) -> AuthUserInfo | None:
        if is_jwt(credential):
            # JSON Web Token auth
            return await self.authorize_user_from_jwt(
                credential, auth_resource, auth_permission
            )
        else:
            # API_KEY auth
            return await self.authorize_user_from_key(
                user_id, credential, auth_resource, auth_permission
            )

    @abstractmethod
    async def authorize_user_from_jwt(
        self, token: str, auth_resource: AuthResource, auth_permission: AuthPermission
    ) -> AuthUserInfo | None:
        # will raise: NotImplementedError
        pass

    @abstractmethod
    async def authorize_user_from_key(
        self,
        user_id: str,
        api_key: str,
        auth_resource: AuthResource,
        auth_permission: AuthPermission,
    ) -> AuthUserInfo | None:
        # will raise: NotImplementedError
        pass


# Core auth handler, verify token on local idp
class CoreAuthHandler(BaseAuthHandler):

    async def authorize_user_from_jwt(
        self, token: str, auth_resource: AuthResource, auth_permission: AuthPermission
    ) -> AuthUserInfo | None:
        try:
            # decode token
            payload = jwt.decode(
                token,
                get_env("CCAT_JWT_SECRET"),
                algorithms=[get_env("CCAT_JWT_ALGORITHM")],
            )

            # get user from DB
            users = get_users()
            if payload["sub"] in users:
                user = users[payload["sub"]]
                # TODOAUTH: permissions check should be done in a method
                if auth_resource in user["permissions"].keys() and \
                        auth_permission in user["permissions"][auth_resource]:
                    return AuthUserInfo(
                        id=payload["sub"],
                        name=payload["username"],
                        permissions=user["permissions"],
                        extra=user,
                    )

        except Exception as e:
            log.error(f"Could not auth user from JWT: {e}")

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

        # TODOAUTH: should we consider the user_id or just give
        #    admin permissions to all users with the right api keys?

        # chatting over websocket
        if auth_resource == AuthResource.CONVERSATION and api_key == ws_api_key:
            return AuthUserInfo(
                id=user_id,
                name=user_id,
                permissions=get_base_permissions()
            )

        # any http endpoint
        if api_key == http_api_key:
            return AuthUserInfo(
                id=user_id,
                name=user_id,
                permissions=get_full_permissions()
            )

        # do not pass
        return None
    
    async def issue_jwt(self, username: str, password: str) -> str | None:
        # authenticate local user credentials and return a JWT token

        # brutal search over users, which are stored in a simple dictionary.
        # waiting to have graph in core to store them properly
        # TODOAUTH: get rid of this shameful loop
        users = get_users()
        for user_id, user in users.items():
            if user["username"] == username and check_password(password, user["password"]):
                # TODOAUTH: expiration with timezone needs to be tested
                # using seconds for easier testing
                expire_delta_in_seconds = float(get_env("CCAT_JWT_EXPIRE_MINUTES")) * 60
                expires = datetime.now(utc) + timedelta(seconds=expire_delta_in_seconds)
                # TODOAUTH: add issuer and redirect_uri (and verify them when a token is validated)

                jwt_content = {
                    "sub": user_id,                      # Subject (the user ID)
                    "username": username,                # Username
                    "permissions": user["permissions"],  # User permissions
                    "exp": expires                       # Expiry date as a Unix timestamp
                }
                return jwt.encode(
                    jwt_content,
                    get_env("CCAT_JWT_SECRET"),
                    algorithm=get_env("CCAT_JWT_ALGORITHM"),
                )
        return None


# Default Auth, always deny auth by default (only core auth decides).
class CoreOnlyAuthHandler(BaseAuthHandler):
    async def authorize_user_from_jwt(*args, **kwargs) -> AuthUserInfo | None:
        return None

    async def authorize_user_from_key(*args, **kwargs) -> AuthUserInfo | None:
        return None


# Api Key Auth, require CCAT_API_KEY usage for admin permissions and CCAT_API_KEY_WS for chat only permission
# TODOAUTH: review
# class ApiKeyAuthHandler(BaseAuthHandler):
#    async def authorize_user_from_token(self, credential: str, auth_resource: AuthResource, auth_permission: AuthPermission) -> AuthUserInfo | None:
#        environment_api_key = get_env("CCAT_API_KEY")
#        environment_public_api_key = get_env("CCAT_API_KEY_WS")
#
#        if auth_resource == AuthResource.CONVERSATION and auth_permission == AuthPermission.WRITE and credential == environment_public_api_key:
#            return AuthUserInfo(
#                user_id="user",
#                user_data={}
#            )
#        if credential == environment_api_key:
#            return AuthUserInfo(
#                user_id="admin",
#                user_data={}
#            )
