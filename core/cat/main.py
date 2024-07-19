import uvicorn
import asyncio
from contextlib import asynccontextmanager
from scalar_fastapi import get_scalar_api_reference

from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from cat.log import log
from cat.env import get_env, fix_legacy_env_variables
from cat.routes import (
    base,
    auth,
    settings,
    llm,
    embedder,
    auth_handler,
    memory,
    plugins,
    upload,
    websocket,
)
from cat.routes.users import users, users_manager
from cat.routes.static import public, admin, static
from cat.routes.openapi import get_openapi_configuration_function
from cat.looking_glass.cheshire_cat import CheshireCat


# TODO: take away in v2
fix_legacy_env_variables()


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
    lifespan=lifespan, generate_unique_id_function=custom_generate_unique_id,
    docs_url=None, redoc_url=None, title="Cheshire-Cat API",
    license_info={"name": "GPL-3", "url": "https://www.gnu.org/licenses/gpl-3.0.en.html"},
)

# Configures the CORS middleware for the FastAPI app
cors_allowed_origins_str = get_env("CCAT_CORS_ALLOWED_ORIGINS")
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
cheshire_cat_api.include_router(auth.router, tags=["User Auth"], prefix="/auth")
cheshire_cat_api.include_router(users.router, tags=["Users"], prefix="/users")
cheshire_cat_api.include_router(users_manager.router, tags=["Users Manager"], prefix="/users-manager")
cheshire_cat_api.include_router(settings.router, tags=["Settings"], prefix="/settings")
cheshire_cat_api.include_router(
    llm.router, tags=["Large Language Model"], prefix="/llm"
)
cheshire_cat_api.include_router(embedder.router, tags=["Embedder"], prefix="/embedder")
cheshire_cat_api.include_router(plugins.router, tags=["Plugins"], prefix="/plugins")
cheshire_cat_api.include_router(memory.router, tags=["Memory"], prefix="/memory")
cheshire_cat_api.include_router(
    upload.router, tags=["Rabbit Hole"], prefix="/rabbithole"
)
cheshire_cat_api.include_router(
    auth_handler.router, tags=["AuthHandler"], prefix="/auth_handler"
)
cheshire_cat_api.include_router(websocket.router, tags=["Websocket"])

# mount static files
# this cannot be done via fastapi.APIrouter:
# https://github.com/tiangolo/fastapi/discussions/9070

# admin single page app (static build)
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

@cheshire_cat_api.get("/docs", include_in_schema=False)
async def scalar_docs():
    return get_scalar_api_reference(
        openapi_url=cheshire_cat_api.openapi_url,
        title=cheshire_cat_api.title,
        scalar_favicon_url="https://cheshirecat.ai/wp-content/uploads/2023/10/Logo-Cheshire-Cat.svg",
    )

# RUN!
if __name__ == "__main__":
    # debugging utilities, to deactivate put `DEBUG=false` in .env
    debug_config = {}
    if get_env("CCAT_DEBUG") == "true":
        debug_config = {
            "reload": True,
            "reload_includes": ["plugin.json"],
            "reload_excludes": ["*test_*.*", "*mock_*.*"],
        }

    uvicorn.run(
        "cat.main:cheshire_cat_api",
        host="0.0.0.0",
        port=80,
        use_colors=True,
        log_level=get_env("CCAT_LOG_LEVEL").lower(),
        **debug_config,
    )
