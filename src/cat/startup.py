from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from cat.env import get_env
from cat.routes import (
    status,
    openapi,
    settings,
    agents,
)

from cat.routes.me import me
from cat.routes.plugins import plugins
from cat.routes.auth import oauth
from cat.routes.auth.default_idp import idp
from cat.looking_glass.cheshire_cat import CheshireCat


@asynccontextmanager
async def lifespan(app: FastAPI):

    #  ^._.^
    ccat = CheshireCat()
    await ccat.bootstrap(app)

    yield


# REST API
cheshire_cat_api = FastAPI(
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    title="Cheshire Cat AI",
    license_info={
        "name": "GPL-3",
        "url": "https://www.gnu.org/licenses/gpl-3.0.en.html",
    },
)

# Configures the CORS middleware for the FastAPI app
cors_enabled = get_env("CCAT_CORS_ENABLED")
if cors_enabled == "true":
    cors_allowed_origins_str = get_env("CCAT_CORS_ALLOWED_ORIGINS")

    # When credentials=True, browsers reject wildcard "*" for Access-Control-Allow-Origin.
    # Using allow_origin_regex=".*" reflects the actual Origin header, which works with credentials.
    if cors_allowed_origins_str in (None, "", "*"):
        cheshire_cat_api.add_middleware(
            CORSMiddleware,
            allow_origin_regex=".*",
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    else:
        origins = cors_allowed_origins_str.split(",")
        cheshire_cat_api.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

# API routers
for r in [
    me, status, settings, agents, oauth,
    plugins
]:
    cheshire_cat_api.include_router(r.router, prefix="/api/v2")

# user facing routers
for r in [ openapi, idp ]:
    cheshire_cat_api.include_router(r.router)
