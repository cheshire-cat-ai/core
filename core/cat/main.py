import os
import re
import json
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from cat.log import log
from cat.routes import base, memory, plugins, upload, websocket
from cat.api_auth import check_api_key
from cat.routes.openapi import get_openapi_configuration_function
from cat.routes.setting import llm_setting, general_setting, embedder_setting
from cat.looking_glass.cheshire_cat import CheshireCat

# import logging
# logging.debug('EXAMPLE with debug category')
# logging.info('EXAMPLE with info category')
# logging.error('EXAMPLE with error category')


@asynccontextmanager
async def lifespan(app: FastAPI):
    #       ^._.^
    #
    # loads Cat and plugins
    # Every endpoint can access the cat instance via request.app.state.ccat
    # - Not using midlleware because I can't make it work with both http and websocket;
    # - Not using Depends because it only supports callables (not instances)
    # - Starlette allows this: https://www.starlette.io/applications/#storing-state-on-the-app-instance
    app.state.ccat = CheshireCat()
    yield


# REST API
cheshire_cat_api = FastAPI(lifespan=lifespan, dependencies=[Depends(check_api_key)])


# Configures the CORS middleware for the FastAPI app
cors_allowed_origins_str = os.getenv("CORS_ALLOWED_ORIGINS", "")
origins = cors_allowed_origins_str.split(",") if cors_allowed_origins_str else ["*"]
cheshire_cat_api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add routers to the middleware stack.
cheshire_cat_api.include_router(base.router, tags=["Status"])
cheshire_cat_api.include_router(general_setting.router, tags=["Settings - General"], prefix="/settings")
cheshire_cat_api.include_router(llm_setting.router, tags=["Settings - Large Language Model"], prefix="/settings/llm")
cheshire_cat_api.include_router(embedder_setting.router, tags=["Settings - Embedder"], prefix="/settings/embedder")
cheshire_cat_api.include_router(plugins.router, tags=["Plugins"], prefix="/plugins")
cheshire_cat_api.include_router(memory.router, tags=["Memory"], prefix="/memory")
cheshire_cat_api.include_router(upload.router, tags=["Rabbit Hole (file upload)"], prefix="/rabbithole")
cheshire_cat_api.include_router(websocket.router, tags=["Websocket"])


# admin index.html
# all the admin files are served in a statci way
# with the exception of index.html that needs a config file derived from core environments variable:
#  - CORE_HOST
#  - CORE_PORT
#  - API_KEY
@cheshire_cat_api.get("/admin/")
def admin_index_injected():

    cat_core_config = json.dumps({
        "CORE_HOST": os.getenv("CORE_HOST"),
        "CORE_PORT": os.getenv("CORE_PORT"),
        "CORE_USE_SECURE_PROTOCOLS": os.getenv("CORE_USE_SECURE_PROTOCOLS"),
        "API_KEY": os.getenv("API_KEY"),
    })

    with open("/admin/dist/index.html", 'r') as f:
        html = f.read()

    # TODO: this is ugly, should be done with beautiful soup or a template
    regex = re.compile(r"catCoreConfig = (\{.*?\})", flags=re.MULTILINE | re.DOTALL)
    default_config = re.search(regex, html).group(1)
    html = html.replace(default_config, cat_core_config)

    return HTMLResponse(html)


# admin (all static files)
# note html=False because index.html needs to be injected with runtime information
cheshire_cat_api.mount("/admin", StaticFiles(directory="/admin/dist/", html=False), name="admin")

# static files (for plugins and other purposes)
# TODO

# error handling
@cheshire_cat_api.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"error": exc.errors()},
    )


# openapi customization
cheshire_cat_api.openapi = get_openapi_configuration_function(cheshire_cat_api)
