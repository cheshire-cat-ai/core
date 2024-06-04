
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
    Base class to build custom Auth systems.
    The framework calls methods `_is_http_allowed` and `_is_ws_allowed`,
    to run environment variables checks; then those two methods call `is_http_allowed` and `is_ws_allowed`
    that MUST be implemented by subclasses.
    """

    @abstractmethod
    def is_http_allowed(self, request: Request):
        pass

    @abstractmethod
    def is_ws_allowed(self, websocket: WebSocket):
        pass


class AuthorizatorCore(BaseAuth):

    def is_http_allowed(self, request: Request):

        # check "Authorization" header
        auth_header = request.headers.get("Authorization")
        if auth_header is None or not auth_header.startswith("Bearer "):
            return False
        
        # verify token
        token = auth_header.split(" ")[1]
        payload = verify_token(token)
        return payload is not None

    def is_ws_allowed(self, websocket: WebSocket):
        
        # verify token
        token = websocket.query_params.get("token")
        payload = verify_token(token)
        return payload is not None
    

# main custom auth (legacy env variables)
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
        

class AuthApiKey(BaseAuth):

    def __init__(self, api_key):
        self.api_key = api_key

    def get_bearer_token(self, request):
        header_value = request.headers.get("Authorization", "")
        return header_value.replace("Bearer", "").strip()

    def is_http_allowed(self, request: Request):
        return self.get_bearer_token(request) == self.api_key

    def is_ws_allowed(self, websocket: WebSocket):
        return websocket.headers.get("Authorization") == self.api_key # TODOAUTH: ws has headers?
