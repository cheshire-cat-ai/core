from urllib.parse import urljoin
from typing import Dict

from fastapi import APIRouter, Request, HTTPException, Body
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field, ValidationError

from cat.auth import User, get_ccat
from cat import urls
from cat.env import get_env


router = APIRouter(prefix="/auth", tags=["Auth"])

# TODOAUTH TODOV2 /token/verify endpoint

@router.get("/logout")
def logout(r: Request) -> RedirectResponse:
    """Logs out the user by clearing the access_token cookie."""

    origin_url = r.headers.get("origin") or r.headers.get("referer") or urls.BASE_URL
    response = RedirectResponse(url=origin_url)
    response.delete_cookie(
        "access_token",
        httponly=True,
        secure="https" in urls.BASE_URL,
        samesite="lax",
    )
    return response

@router.get("/login/{name}")
async def oauth_login(
    r: Request,
    name: str,
    ccat=get_ccat(),
) -> RedirectResponse:
    """Starts the OAuth flow."""
    ahs = await ccat.get_all("auths")
    auth = ahs.get(name, None)
    
    if auth is None:
        raise HTTPException(status_code=404, detail=f"Auth Handler {name} not found.")
    

    redirect_uri = urljoin(urls.API_URL, f"auth/callback/{name}")
    origin_url = r.headers.get("origin") or r.headers.get("referer") or urls.BASE_URL
    
    # start OAuth flow and set origin cookie so callback can redirect back
    response = RedirectResponse(
        url = await auth.get_provider_login_url(redirect_uri)
    )
    response.set_cookie(
        "origin_url",
        origin_url,
        httponly=True,
        secure="https" in urls.BASE_URL,
        samesite="lax",
        max_age=300,
    )
    return response

@router.get("/callback/{name}")
async def oauth_callback(r: Request, name: str, ccat=get_ccat()):
    """OAuth callback."""

    ahs = await ccat.get_all("auths")
    auth = ahs.get(name, None)

    if auth is None:
        raise HTTPException(
            status_code=404,
            detail=f"Auth Handler {name} not found."
        )

    redirect_uri = urljoin(urls.API_URL, f"auth/callback/{name}")

    user = await auth.authorize_user_from_oauth_code(
        redirect_uri,
        dict(r.query_params)
    )
    if user is None:
        raise HTTPException(
            status_code=403,
            detail=f"Auth Handler {name} could not complete the OAuth flow."
        )

    token = auth.jwt.encode(user)

   # read origin cookie (fallback to base_url), then remove it and set JWT cookie
    origin_url = r.cookies.get("origin_url") or urls.BASE_URL
    response = RedirectResponse(origin_url)
    response.delete_cookie(
        "origin_url",
        samesite="lax",
        secure="https" in urls.BASE_URL
    )
    response.set_cookie(
        "access_token",
        token,
        httponly=True,
        secure="https" in urls.BASE_URL,
        samesite="lax",
        max_age=int( get_env("CCAT_JWT_EXPIRE_MINUTES") ) * 60,
    )
    return response


