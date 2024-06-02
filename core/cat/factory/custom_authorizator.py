from abc import ABC, abstractmethod

from fastapi import (
    WebSocket,
    Request,
    HTTPException
)

from cat.env import get_env
from cat.log import log

class BaseAuth(ABC):
    """
    Base class to build custom Auth systems.
    The framework calls methods `_is_http_allowed` and `_is_ws_allowed`,
    to run default checks; then those two methods call `is_http_allowed` and `is_ws_allowed`
    that MUST be implemented by subclasses.
    """

    def _is_http_allowed(self, request: Request):

        # internal auth system for the admin panel
        # TODOAUTH

        # Default protection for http via CCAT_API_KEY env variable.
        environment_api_key = get_env("CCAT_API_KEY")

        # env not set, delegate to custom authenticator
        if environment_api_key is None:
            return self.is_http_allowed(request)

        # both env and custom authenticator must allow access
        correct_key = request.headers.get("access_token") == environment_api_key
        return correct_key and self.is_http_allowed(request)

    def _is_ws_allowed(self, websocket: WebSocket):

        # internal auth system for the admin panel
        # TODOAUTH

        # this method here in case we'll need default/mandatory/legacy behaviour for websocket
        return self.is_ws_allowed(websocket)

    @abstractmethod
    def is_http_allowed(self, request: Request):
        pass

    @abstractmethod
    def is_ws_allowed(self, websocket: WebSocket):
        pass


class AuthorizatorNoAuth(BaseAuth):
    def __init__(self):
        pass

    def is_http_allowed(self, request: Request):
        # Here we let anything pass.
        # Note CCAT_API_KEY is still respected (see super()._is_http_allowed)
        return True

    def is_ws_allowed(self, websocket: WebSocket):
        return True


class AuthorizatorApiKey(BaseAuth):

    def __init__(self, api_key):
        self.api_key = api_key

    def is_http_allowed(self, request: Request):
        return request.headers.get("Authorization") == self.api_key

    def is_ws_allowed(self, websocket: WebSocket):
        return websocket.headers.get("Authorization") == self.api_key # TODOAUTH: ws has headers?
