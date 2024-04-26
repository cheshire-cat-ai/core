from os import getenv
from fastapi import (
    WebSocket,
    Request,
    HTTPException
)

from cat.log import log

class BaseAuth():
    def __init__(self):
        self.master_key = getenv("API_KEY")

    def is_master_key(self, request):
        if self.is_master_key == None:
            return True
        return request.headers.get("access_token") == self.master_key
    
    def is_http_allowed(self, request):
        return self.is_master_key(request)
    
    def is_ws_allowed(self, websocket):
        return True
    
class AuthorizatorNoAuth(BaseAuth):
    def __init__(self):
        pass

    def is_master_key(self, request):
        return True

    def is_http_allowed(self, request: Request):
        return True
    
    def is_ws_allowed(self, websocket: WebSocket):
        return True

class AuthorizatorApiKey(BaseAuth):
    def __init__(self, api_key):
        self.api_key = api_key
        super().__init__()

    def is_master_key(self, request):
        if self.master_key == None:
            raise HTTPException(
                status_code=403,
                detail={"error": "Master key is not set"}
            )
        return super().is_master_key(request)
    
    def is_http_allowed(self, request: Request):
        if request.headers.get("Authorization") != self.api_key:
            raise HTTPException(
                status_code=403,
                detail={"error": "Invalid API Key"}
            )
        return True

    def is_ws_allowed(self, websocket: WebSocket):
        if websocket.headers.get("Authorization") != self.api_key:
            raise HTTPException(
                status_code=403,
                detail={"error": "Invalid API Key"}
            )
        return True
