
from abc import ABC, abstractmethod

from fastapi import (
    WebSocket,
    Request,
    HTTPException
)

from cat.auth.jwt import verify_token
from cat.env import get_env
from cat.log import log


class BaseAuth(ABC): # TODOAUTH: pydantic model?
    """
    Base class to build custom Auth systems that will live alongside core auth.
    Methods `is_http_allowed` and `is_ws_allowed`
    MUST be implemented by subclasses.
    """

    @abstractmethod
    def is_http_allowed(self, request: Request):
        pass

    @abstractmethod
    def is_ws_allowed(self, websocket: WebSocket):
        pass


# Internal Auth, used as a standard for the admin panel and other community clients.
class AuthCore(BaseAuth):

    def is_http_allowed(self, request: Request):

        # check "Authorization" header
        auth_header = request.headers.get("Authorization")
        if auth_header is None or not auth_header.startswith("Bearer "):
            return False
        
        # verify token
        token = auth_header.split(" ")[1]
        return verify_token(token)

    def is_ws_allowed(self, websocket: WebSocket):

        # verify token
        token = websocket.query_params.get("token")
        return verify_token(token)
    

# Main custom auth (legacy env variables)
class AuthEnvironmentVariables(BaseAuth):

    def is_http_allowed(self, request: Request):
        
        # Protect http endpoints via CCAT_API_KEY env variable.
        environment_api_key = get_env("CCAT_API_KEY")
        
        # env not set, just pass
        if environment_api_key is None:
            return True
        
        # env is set, must be same as header `access_token`
        return request.headers.get("access_token") == environment_api_key
        
    def is_ws_allowed(self, websocket: WebSocket):

        # Protect websockets via CCAT_API_KEY_WS env variable.
        environment_api_key_ws = get_env("CCAT_API_KEY_WS")

        # env not set, just pass
        if environment_api_key_ws is None:
            return True
        
         
        # env is set, must be same as query param `access_token`
        return websocket.query_params.get("access_token") == environment_api_key_ws
        

# Set http and ws keys directly into the admin settings
class AuthApiKey(BaseAuth):

    def __init__(self, api_key_http=None, api_key_ws=None):
        self.api_key_http = api_key_http
        self.api_key_ws = api_key_ws

    def is_http_allowed(self, request: Request):
        return request.headers.get("access_token") == self.api_key_http

    def is_ws_allowed(self, websocket: WebSocket):
        return websocket.query_params.get("access_token") == self.api_key_ws
