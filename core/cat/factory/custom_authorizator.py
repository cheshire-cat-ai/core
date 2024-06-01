from os import getenv
from fastapi import (
    WebSocket,
    Request,
    HTTPException
)

from cat.log import log


# TODOAUTH Abstract Auth class
# https://github.com/cheshire-cat-ai/core/pull/794#issuecomment-2085127185

class BaseAuth():
    def __init__(self):
        self.api_key = getenv("CCAT_API_KEY")
    
    def is_http_allowed(self, request):
        # default http is protected via CCAT_API_KEY env variable
        if self.api_key == None:
            return True
        return request.headers.get("access_token") == self.api_key
    
    def is_ws_allowed(self, websocket):
        # default ws is open
        return True

class AuthorizatorNoAuth(BaseAuth):
    def __init__(self):
        pass

    def is_http_allowed(self, request: Request):
        return True
    
    def is_ws_allowed(self, websocket: WebSocket):
        return True

class AuthorizatorApiKey(BaseAuth):
    def __init__(self, api_key):
        self.api_key = api_key
        super().__init__() # TODOAUTH ??? why call parent constructor?
    
    def is_http_allowed(self, request: Request):
        if request.headers.get("Authorization") != self.api_key:
            raise HTTPException(
                status_code=403,
                detail={"error": "Invalid API Key"}
            )
        return True

    def is_ws_allowed(self, websocket: WebSocket):
        if websocket.headers.get("Authorization") != self.api_key: # TODOAUTH: ws has no headers from the browser?
            raise HTTPException(
                status_code=403,
                detail={"error": "Invalid API Key"}
            )
        return True
