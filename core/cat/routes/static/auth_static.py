from fastapi.staticfiles import StaticFiles
from fastapi import Request
from cat.auth.headers import http_auth

class AuthStatic(StaticFiles):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    async def __call__(self, scope, receive, send) -> None:
        request = Request(scope, receive=receive)
        http_auth(request) # TODOAUTH: verify static files follow the auth
        await super().__call__(scope, receive, send)