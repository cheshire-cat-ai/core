from fastapi.staticfiles import StaticFiles
#from fastapi import Request, HTTPException

from cat import utils
#from cat.auth.connection import HTTPAuth
#from cat.auth.permissions import AuthPermission, AuthResource


# disabling auth for static files at the moment
# TODOV2: should this be under auth?
# class AuthStatic(StaticFiles):
#     def __init__(self, *args, **kwargs) -> None:
#         super().__init__(*args, **kwargs)

#     async def __call__(self, scope, receive, send) -> None:
#         request = Request(scope, receive=receive)
#         http_auth = HTTPAuth(
#             resource=AuthResource.STATIC, permission=AuthPermission.READ
#         )
#         allowed = False
#         async for permission in http_auth(request):
#             allowed = permission
#             break
#         if allowed:
#             await super().__call__(scope, receive, send)
#         else:
#             raise HTTPException(status_code=403, detail={"error": "Forbidden."})


def mount(cheshire_cat_api):
    # static files folder available to plugins
    # TODOAUTH: test static files auth
    static_dir = utils.get_base_path() + "static"
    cheshire_cat_api.mount(
        "/static/", StaticFiles(directory=static_dir), name="static"
    )

    # internal static files folder
    core_static_dir = utils.get_base_path() + "routes/static/core_static_folder"
    cheshire_cat_api.mount(
        "/core-static/",
        StaticFiles(directory=core_static_dir),
        name="core-static",
    )
