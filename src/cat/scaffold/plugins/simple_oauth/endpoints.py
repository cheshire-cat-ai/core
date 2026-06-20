"""The login flow, as plugin endpoints.

Generic OAuth routes — `/auth/login/{name}`, `/auth/callback/{name}`,
`/auth/logout` — that dispatch to any registered `Auth` handler by slug, plus a
built-in mock identity provider page used by the `simple` handler for local dev.

Core knows none of this; it only verifies the JWT we set as a cookie at the end
of `/auth/callback`. The routes are open (no `role=`) because logging in must be
reachable before you are authenticated.
"""

import os
import hashlib

from fastapi import Request, HTTPException, Form
from fastapi.responses import RedirectResponse, HTMLResponse

from cat import endpoint, config
from cat.context import ccat


@endpoint.get("/auth/login/{name}", tags=["Auth"])
async def oauth_login(r: Request, name: str) -> RedirectResponse:
    """Start the OAuth flow for the named handler."""
    ahs = await ccat().get_all("auths")
    auth = ahs.get(name)
    if auth is None:
        raise HTTPException(status_code=404, detail=f"Auth Handler {name} not found.")

    redirect_uri = f"{config.URL}/auth/callback/{name}"
    origin_url = r.headers.get("origin") or r.headers.get("referer") or config.URL

    # start the flow and remember where to send the user back after callback
    response = RedirectResponse(url=await auth.get_provider_login_url(redirect_uri))
    response.set_cookie(
        "origin_url",
        origin_url,
        httponly=True,
        secure="https" in config.URL,
        samesite="lax",
        max_age=300,
    )
    return response


@endpoint.get("/auth/callback/{name}", tags=["Auth"])
async def oauth_callback(r: Request, name: str):
    """Finish the OAuth flow: map the provider code to a user, mint a core JWT."""
    ahs = await ccat().get_all("auths")
    auth = ahs.get(name)
    if auth is None:
        raise HTTPException(status_code=404, detail=f"Auth Handler {name} not found.")

    redirect_uri = f"{config.URL}/auth/callback/{name}"
    user = await auth.authorize_user_from_oauth_code(redirect_uri, dict(r.query_params))
    if user is None:
        raise HTTPException(
            status_code=403,
            detail=f"Auth Handler {name} could not complete the OAuth flow.",
        )

    # the session token core will trust from now on
    token = auth.jwt.encode(user)

    origin_url = r.cookies.get("origin_url") or config.URL
    response = RedirectResponse(origin_url)
    response.delete_cookie("origin_url", samesite="lax", secure="https" in config.URL)
    response.set_cookie(
        "access_token",
        token,
        httponly=True,
        secure="https" in config.URL,
        samesite="lax",
        max_age=int(config.JWT_EXPIRE_MINUTES) * 60,
    )
    return response


@endpoint.get("/auth/logout", tags=["Auth"])
def oauth_logout(r: Request) -> RedirectResponse:
    """Clear the session cookie."""
    origin_url = r.headers.get("origin") or r.headers.get("referer") or config.URL
    response = RedirectResponse(url=origin_url)
    response.delete_cookie(
        "access_token",
        httponly=True,
        secure="https" in config.URL,
        samesite="lax",
    )
    return response


# --- the built-in mock identity provider (development only) ----------------

@endpoint.get("/auth/internal-idp", include_in_schema=False)
async def internal_idp(redirect_uri: str) -> HTMLResponse:
    """Serve the mock login page."""
    html_path = os.path.join(os.path.dirname(__file__), "idp.html")
    with open(html_path, "r") as f:
        html = f.read()
    return HTMLResponse(html.replace("{{redirect_uri}}", redirect_uri))


@endpoint.post("/auth/internal-idp/login", include_in_schema=False)
async def internal_idp_login(api_key: str = Form(...), redirect_uri: str = Form(...)):
    """Mock IdP: if the API key matches, redirect back with an auth code."""
    if api_key == config.API_KEY:
        code = hashlib.sha256(api_key.encode()).hexdigest()[:16]
        return RedirectResponse(url=f"{redirect_uri}?code={code}", status_code=303)
    return RedirectResponse(
        url=f"/auth/internal-idp?redirect_uri={redirect_uri}", status_code=303
    )
