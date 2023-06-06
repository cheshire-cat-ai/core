
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse


def mount(cheshire_cat_api):

    # note html=False because index.html needs to be injected with runtime information
    cheshire_cat_api.mount("/public/", StaticFiles(directory="cat/public/", html=True), name="chat")



