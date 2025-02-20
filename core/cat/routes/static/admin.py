from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import Depends

from cat.auth.permissions import AuthResource, AuthPermission
from cat.auth.connection import CoreFrontendAuth
from cat.looking_glass.stray_cat import StrayCat


def mount(cheshire_cat_api):
    # mount admin Single Page App (static build downloaded from the admin-vue repo)
    mount_admin_spa(cheshire_cat_api)

    # note html=False because index.html needs to be injected with runtime information
    cheshire_cat_api.mount("/admin", StaticFiles(directory="/admin/"), name="admin")


def mount_admin_spa(cheshire_cat_api):
    @cheshire_cat_api.get("/admin/", include_in_schema=False)
    @cheshire_cat_api.get("/admin/{page}", include_in_schema=False)
    @cheshire_cat_api.get("/admin/{page}/", include_in_schema=False)
    def get_admin_single_page_app(
        cat: StrayCat = Depends(
            CoreFrontendAuth(AuthResource.STATIC, AuthPermission.READ)
        )
    ):

        # the admin static build is created during docker build from this repo:
        # https://github.com/cheshire-cat-ai/admin-vue
        # the files live inside the /admin folder (not visible in volume / cat code)
        return FileResponse("/admin/index.html")
