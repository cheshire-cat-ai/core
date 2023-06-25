from cat.routes.static.auth_static import AuthStatic

def mount(cheshire_cat_api):
    cheshire_cat_api.mount("/static/", AuthStatic(directory="cat/static"), name="static")

