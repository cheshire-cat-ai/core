import traceback

from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Body, Query, Request

from cat.utils import log
from cat.routes import setting, memory, base, websocket, upload
from cat.routes.openapi import get_openapi_configuration_function
from cat.looking_glass.cheshire_cat import CheshireCat

#       ^._.^
#
# loads Cat and plugins
cheshire_cat = CheshireCat()


# REST API
cheshire_cat_api = FastAPI()
    

# Every endpoint can access the cat instance via request.app.state.ccat
# - Not using midlleware because I can't make it work with both http and websocket;
# - Not using Depends because it only supports callables (not instances)
# - Starlette allows this: https://www.starlette.io/applications/#storing-state-on-the-app-instance
cheshire_cat_api.state.ccat = cheshire_cat


# list of allowed CORS origins.
# This list allows any domain to make requests to the server,
# including sending cookies and using any HTTP method and header.
# Whilst this is useful in dev environments, it might be too permissive for production environments
# therefore, it might be a good idea to configure the allowed origins in a differnet configuration file
origins = ["*"]  # TODO: add CORS_ALLOWED_ORIGINS support from .env

# Configures the CORS middleware for the FastAPI app
cheshire_cat_api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add routers to the middleware stack.
cheshire_cat_api.include_router(base.router, tags=["Base"])
cheshire_cat_api.include_router(setting.router, tags=["Settings"], prefix="/settings")
cheshire_cat_api.include_router(memory.router, tags=["Memory"], prefix="/memory")
cheshire_cat_api.include_router(upload.router, tags=["Rabbit Hole (file upload)"], prefix="/rabbithole")
cheshire_cat_api.include_router(websocket.router, tags=["Websocket"])

# error handling
@cheshire_cat_api.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"error": exc.errors()},
    )

# openapi customization
cheshire_cat_api.openapi = get_openapi_configuration_function(cheshire_cat_api)






