import os
import re
import json
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse


def mount(cheshire_cat_api):

    # mount admin Single Page App (static build downloaded from the admin-vue repo)
    mount_admin_spa(cheshire_cat_api)

    # note html=False because index.html needs to be injected with runtime information
    cheshire_cat_api.mount("/admin", StaticFiles(directory="/admin/", html=False), name="admin")


def mount_admin_spa(cheshire_cat_api):
    @cheshire_cat_api.get("/admin/")
    @cheshire_cat_api.get("/admin/{page}")
    @cheshire_cat_api.get("/admin/{page}/")
    def get_injected_admin():

        # the admin static build is created during docker build from this repo:
        # https://github.com/cheshire-cat-ai/admin-vue
        # the files live inside the /admin folder (not visible in volume / cat code)
        with open("/admin/index.html", 'r') as f:
            html = f.read()

        return HTMLResponse(html)


