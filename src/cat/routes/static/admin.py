
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import Depends

from cat import utils
from cat.auth.permissions import AuthResource, AuthPermission
from cat.auth.connection import CoreFrontendAuth
from cat.looking_glass.stray_cat import StrayCat


def mount(cheshire_cat_api):
    # mount admin Single Page App (static build downloaded from the admin-vue repo)
    mount_admin_spa(cheshire_cat_api)

    # note html=False because index.html needs to be injected with runtime information
    admin_dir = utils.get_base_path() + "routes/static/core_static_folder/admin"
    
    import os
    print("\n\n\n99999999999999 ", os.path.dirname(__file__))
    
    cheshire_cat_api.mount("/admin", StaticFiles(directory=admin_dir), name="admin")


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
        return FileResponse(
            utils.get_base_path() + "routes/static/core_static_folder/admin/index.html"
        )
