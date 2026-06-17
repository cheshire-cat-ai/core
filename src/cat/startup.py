from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from cat import config
from cat.context import Ctx, set_ctx, reset_ctx
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


class RequestContextMiddleware:
    """
    Pure-ASGI middleware that authenticates each request and populates the
    per-request `Ctx` (user + stream slot) in a contextvar.

    Pure ASGI (not BaseHTTPMiddleware) so the contextvar is set in the *same*
    async context the endpoint runs in — BaseHTTPMiddleware would set it in a
    separate task and the endpoint would not see it. Authentication is
    best-effort: public routes simply get `user = None`.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        from cat.capabilities import auth

        request = Request(scope, receive)
        try:
            user = await auth(request)
        except Exception:
            user = None

        token = set_ctx(Ctx(user=user, request=request))
        try:
            await self.app(scope, receive, send)
        finally:
            reset_ctx(token)


def create_app() -> FastAPI:
    """Build a fresh Cheshire Cat FastAPI application.

    A factory (not a module-level singleton) so each test gets an isolated app
    with its own routes and lifespan, while production still uses the single
    `cheshire_cat_api` instance below.
    """
    app = FastAPI(
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        title="Cheshire Cat AI",
        license_info={
            "name": "GPL-3",
            "url": "https://www.gnu.org/licenses/gpl-3.0.en.html",
        },
    )

    # Populate the per-request context (user + stream) for every request.
    # Added before CORS so CORS stays the outermost layer (handles preflight).
    app.add_middleware(RequestContextMiddleware)

    # Configures the CORS middleware for the FastAPI app
    if config.CORS_ENABLED:
        cors_allowed_origins_str = config.CORS_ALLOWED_ORIGINS

        # When credentials=True, browsers reject wildcard "*" for Access-Control-Allow-Origin.
        # Using allow_origin_regex=".*" reflects the actual Origin header, which works with credentials.
        if cors_allowed_origins_str in (None, "", "*"):
            app.add_middleware(
                CORSMiddleware,
                allow_origin_regex=".*",
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        else:
            origins = cors_allowed_origins_str.split(",")
            app.add_middleware(
                CORSMiddleware,
                allow_origins=origins,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

    # all routers mounted at root (no API prefix)
    for r in [
        me, status, settings, agents, oauth,
        plugins, openapi, idp
    ]:
        app.include_router(r.router)

    return app


# REST API — the single production instance (uvicorn targets this).
cheshire_cat_api = create_app()
