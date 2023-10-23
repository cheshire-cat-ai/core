from fastapi.staticfiles import StaticFiles
from fastapi import Request
from cat.headers import check_api_key

class AuthStatic(StaticFiles):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    async def __call__(self, scope, receive, send) -> None:
        request = Request(scope, receive=receive)
        check_api_key(request.headers.get("access_token"))
        await super().__call__(scope, receive, send)