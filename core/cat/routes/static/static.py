from fastapi import Request, HTTPException
from fastapi.staticfiles import StaticFiles

from cat.auth.headers import http_auth
from cat.auth.utils import AuthPermission, AuthResource


class AuthStatic(StaticFiles):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    async def __call__(self, scope, receive, send) -> None:
        request = Request(scope, receive=receive)
        stray_http_auth = http_auth(
            permission=AuthPermission.READ, resource=AuthResource.STATIC
        )
        allowed = await stray_http_auth(request)
        if allowed:
            await super().__call__(scope, receive, send)
        else:
            raise HTTPException(status_code=403, detail={"error": "Forbidden."})


def mount(cheshire_cat_api):
    # static files folder available to plugins
    # TODOAUTH: test static files auth
    cheshire_cat_api.mount(
        "/static/", AuthStatic(directory="cat/static"), name="static"
    )

    # internal static files folder
    cheshire_cat_api.mount(
        "/core-static/",
        StaticFiles(directory="cat/routes/static/core_static_folder/"),
        name="core-static",
    )
