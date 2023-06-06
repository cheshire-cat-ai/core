from fastapi.staticfiles import StaticFiles

def mount(cheshire_cat_api):
    cheshire_cat_api.mount("/static/", StaticFiles(directory="cat/static"), name="static")

