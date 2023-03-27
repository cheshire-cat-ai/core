import traceback

from cat.routes import setting, memory, base, websocket, upload
from fastapi import FastAPI, Body, Query, Request
from cat.utils import log
from cat.rabbit_hole import (  # TODO: should be moved inside the cat as a method?
    ingest_file,
)
from cat.looking_glass.cheshire_cat import CheshireCat
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware

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


# Configure openAPI schema for swagger and redoc
def custom_openapi():
    if cheshire_cat_api.openapi_schema:
        return cheshire_cat_api.openapi_schema
    openapi_schema = get_openapi(
        title="😸 Cheshire-Cat API",
        version="0.1 (beta)",
        # TODO: this description should be more descriptive about the APIs capabilities
        description="Customizable AI architecture",
        routes=cheshire_cat_api.routes,
    )
    # Image should be an url and it's mostly used for redoc
    openapi_schema["info"]["x-logo"] = {
        "url": "https://github.com/pieroit/cheshire-cat/blob/main/cheshire-cat.jpeg?raw=true"
    }
    # Defines preconfigured examples for swagger
    # This example set parameter of /settings/ get: 'limit' to 3, page to 2 and search to "XYZ"
    # openapi_schema["paths"]["/settings/"]["get"]["parameters"][0]["example"] = 3
    # openapi_schema["paths"]["/settings/"]["get"]["parameters"][0]["example"] = 2
    # openapi_schema["paths"]["/settings/"]["get"]["parameters"][2]["example"] = "XYZ"
    cheshire_cat_api.openapi_schema = openapi_schema
    return cheshire_cat_api.openapi_schema


cheshire_cat_api.openapi = custom_openapi
