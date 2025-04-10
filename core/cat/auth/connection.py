# Helper classes for connection handling
# Credential extraction from ws / http connections is not delegated to the custom auth handlers,
#  to have a standard auth interface.

from abc import ABC, abstractmethod
from typing import Tuple, AsyncGenerator
from urllib.parse import urlencode

from fastapi import (
    Request,
    WebSocket,
    HTTPException,
    WebSocketException,
)
from fastapi.requests import HTTPConnection

from cat.auth.permissions import (
    AuthPermission,
    AuthResource,
    AuthUserInfo,
)
from cat.looking_glass.stray_cat import StrayCat
from cat.log import log


class ConnectionAuth(ABC):

    def __init__(
            self,
            resource: AuthResource,
            permission: AuthPermission):
        
        self.resource = resource
        self.permission = permission

    async def __call__(
        self,
        connection: HTTPConnection # Request | WebSocket,
    ) -> AsyncGenerator[StrayCat, None]:

        # get protocol from Starlette request
        protocol = connection.scope.get('type')
        # extract credentials (user_id, token_or_key) from connection
        user_id, credential = self.extract_credentials(connection)
        auth_handlers = [
            # try to get user from auth_handler
            connection.app.state.ccat.custom_auth_handler,
            # try to get user from local idp
            connection.app.state.ccat.core_auth_handler,
        ]
        for ah in auth_handlers:
            user: AuthUserInfo = ah.authorize_user_from_credential(
                protocol, credential, self.resource, self.permission, user_id=user_id
            )
            if user:
                # create new StrayCat
                cat = StrayCat(user)
                
                # StrayCat is passed to the endpoint
                yield cat

                # save working memory and delete StrayCat after endpoint execution
                cat.update_working_memory_cache()
                del cat
                return

        # if no StrayCat was obtained, raise exception
        self.not_allowed(connection)

    @abstractmethod
    def extract_credentials(self, connection: Request | WebSocket) -> Tuple[str] | None:
        pass

    @abstractmethod
    def not_allowed(self, connection: Request | WebSocket):
        pass
        

class HTTPAuth(ConnectionAuth):

    def extract_credentials(self, connection: Request) -> Tuple[str, str] | None:
        """
        Extract user_id and token/key from headers
        """

        # when using CCAT_API_KEY, user_id is passed in headers
        user_id = connection.headers.get("user_id", "user")

        # Proper Authorization header
        token = connection.headers.get("Authorization", None)
        if token and ("Bearer " in token):
            token = token.replace("Bearer ", "")

        if not token:
            # Legacy header to pass CCAT_API_KEY
            token = connection.headers.get("access_token", None)
            if token:
                log.warning(
                    "Deprecation Warning: `access_token` header will not be supported in v2."
                    "Pass your token/key using the `Authorization: Bearer <token>` format."
                )
        
        # some clients may send an empty string instead of just not setting the header
        if token == "":
            token = None

        return user_id, token


    def not_allowed(self, connection: Request):
        raise HTTPException(status_code=403, detail={"error": "Invalid Credentials"})
    

    

class WebSocketAuth(ConnectionAuth):

    def extract_credentials(self, connection: WebSocket) -> Tuple[str, str] | None:
        """
        Extract user_id from WebSocket path params
        Extract token from WebSocket query string
        """
        user_id = connection.path_params.get("user_id", "user")

        # TODOAUTH: is there a more secure way to pass the token over websocket?
        #   Headers do not work from the browser
        token = connection.query_params.get("token", None)
        
        return user_id, token

    def not_allowed(self, connection: WebSocket):
        raise WebSocketException(code=1004, reason="Invalid Credentials")



class CoreFrontendAuth(HTTPAuth):

    def extract_credentials(self, connection: Request) -> Tuple[str, str] | None:
        """
        Extract user_id from cookie
        """

        token = connection.cookies.get("ccat_user_token", None)

        # core webapps cannot be accessed without a cookie
        if token is None or token == "":
            self.not_allowed(connection)

        return "user", token
    
    def not_allowed(self, connection: Request):
        referer_query = urlencode({"referer": connection.url.path})
        raise HTTPException(
            status_code=307,
            headers={
                "Location": f"/auth/login?{referer_query}"
            }
        )