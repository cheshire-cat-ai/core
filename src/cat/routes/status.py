from typing import Dict
from importlib import metadata
from pydantic import BaseModel

from fastapi import APIRouter

from cat.context import ccat
from cat.services.auths.base import Auth

router = APIRouter(prefix="/status", tags=["Status"])


class AuthHandlerResponse(BaseModel):
    slug: str
    name: str | None
    description: str | None
    # Whether this handler offers an OAuth login flow (a "login with ..." button),
    # and where to start it. None when the handler only verifies credentials.
    login_url: str | None = None


class StatusResponse(BaseModel):
    status: str
    version: str
    auth_handlers: Dict[str, AuthHandlerResponse]


@router.get("")
async def status() -> StatusResponse:
    """Server status. Public on purpose: an unauthenticated single-page app reads
    `auth_handlers` from here to render its "login with ..." options."""

    ahs = await ccat().get_all("auths")

    return StatusResponse(
        status="We're all mad here, dear!",
        version=metadata.version("cheshire-cat-ai"),
        auth_handlers={
            slug: AuthHandlerResponse(
                slug=ah.slug,
                name=ah.name,
                description=ah.description,
                # A handler offers login if it overrides the base stub. The login
                # route itself is provided by a login plugin, by convention.
                login_url=(
                    f"/auth/login/{ah.slug}"
                    if type(ah).get_provider_login_url is not Auth.get_provider_login_url
                    else None
                ),
            )
            for slug, ah in ahs.items()
        },
    )


