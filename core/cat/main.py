import os
from contextlib import asynccontextmanager
import asyncio
import uvicorn

from fastapi import Depends, FastAPI
from fastapi.routing import APIRoute
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from cat.log import log
from cat.routes import base, settings, llm, embedder, memory, plugins, upload, websocket 
from cat.routes.static import public, admin, static
from cat.headers import check_api_key
from cat.routes.openapi import get_openapi_configuration_function
from cat.looking_glass.cheshire_cat import CheshireCat 


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

    # Dict of pseudo-sessions (key is the user_id)
    app.state.strays = {}

    # set a reference to asyncio event loop
    app.state.event_loop = asyncio.get_running_loop()

    # startup message with admin, public and swagger addresses
    log.welcome()

    yield


def custom_generate_unique_id(route: APIRoute):
    return f"{route.name}"


# REST API
cheshire_cat_api = FastAPI(
    lifespan=lifespan,
    generate_unique_id_function=custom_generate_unique_id
)

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
cheshire_cat_api.include_router(base.router, tags=["Status"], dependencies=[Depends(check_api_key)])
cheshire_cat_api.include_router(settings.router, tags=["Settings"], prefix="/settings", dependencies=[Depends(check_api_key)])
cheshire_cat_api.include_router(llm.router, tags=["Large Language Model"], prefix="/llm", dependencies=[Depends(check_api_key)])
cheshire_cat_api.include_router(embedder.router, tags=["Embedder"], prefix="/embedder", dependencies=[Depends(check_api_key)])
cheshire_cat_api.include_router(plugins.router, tags=["Plugins"], prefix="/plugins", dependencies=[Depends(check_api_key)])
cheshire_cat_api.include_router(memory.router, tags=["Memory"], prefix="/memory", dependencies=[Depends(check_api_key)])
cheshire_cat_api.include_router(upload.router, tags=["Rabbit Hole"], prefix="/rabbithole", dependencies=[Depends(check_api_key)])
cheshire_cat_api.include_router(websocket.router, tags=["WebSocket"])

# mount static files
# this cannot be done via fastapi.APIrouter:
# https://github.com/tiangolo/fastapi/discussions/9070
# admin single page app
admin.mount_admin_spa(cheshire_cat_api)
# admin (static build)
admin.mount(cheshire_cat_api)
# static files (for plugins and other purposes)
static.mount(cheshire_cat_api)
# static files for hackable chat in cat/public
public.mount(cheshire_cat_api)


# error handling
@cheshire_cat_api.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"error": exc.errors()},
    )


# openapi customization
cheshire_cat_api.openapi = get_openapi_configuration_function(cheshire_cat_api)

# RUN!
if __name__ == "__main__":

    # debugging utilities, to deactivate put `DEBUG=false` in .env
    debug_config = {}
    if os.getenv("DEBUG", "true") == "true":
        debug_config = {
            "reload": True,
            "reload_includes": ["plugin.json"],
            "reload_excludes": ["*test_*.*", "*mock_*.*"]
        }

    log_level = os.getenv("LOG_LEVEL", "info")
    uvicorn.run(
        "cat.main:cheshire_cat_api",
        host="0.0.0.0",
        port=80,
        use_colors=True,
        log_level=log_level.lower(),
        **debug_config
    )
