from pytz import utc
import asyncio
from urllib.parse import urlencode
from datetime import datetime, timedelta
import jwt
from pydantic import BaseModel

from fastapi import APIRouter, Request, HTTPException, Response, status, Query
from fastapi.responses import RedirectResponse


# from cat.auth.jwt import create_access_token
from cat.db.crud import get_users
from cat.env import get_env
from cat.routes.static.templates import get_jinja_templates


router = APIRouter()

class UserCredentials(BaseModel):
    username: str
    password: str

class JWTResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# set cookies and redirect to origin page after login
@router.post("/redirect", include_in_schema=False)
async def core_login_token(request: Request, response: Response):
    # get form data from submitted core login form (/auth/core_login)
    form_data = await request.form()

    # use username and password to authenticate user from local identity provider and get token
    access_token = await authenticate_local_user(
        form_data["username"], form_data["password"]
    )

    if access_token:
        response = RedirectResponse(
            url=form_data["referer"], status_code=status.HTTP_303_SEE_OTHER
        )
        response.set_cookie(key="ccat_user_token", value=access_token)
        return response

    # credentials are wrong, wait a second (for brute force attacks) and go back to login
    await asyncio.sleep(1)
    referer_query = urlencode(
        {
            "referer": form_data["referer"],
            "retry": 1,
        }
    )
    login_url = f"/auth/login?{referer_query}"
    response = RedirectResponse(url=login_url, status_code=status.HTTP_303_SEE_OTHER)
    return response


@router.get("/login", include_in_schema=False)
async def auth_index(
    request: Request, referer: str = Query(None), retry: int = Query(0)
):
    """Core login form, used when no external Identity Provider is configured"""

    error_message = ""
    if retry == 1:
        error_message = "Invalid Credentials"

    if referer is None:
        referer = "/admin/"

    templates = get_jinja_templates()
    template_context = {"referer": referer, "error_message": error_message}
    return templates.TemplateResponse(
        request=request, name="auth/login.html", context=template_context
    )


# TODOAUTH /logout endpoint


@router.post("/token")
async def auth_token(credentials: UserCredentials):
    """Endpoint called from client to get a JWT from local identity provider.
    This endpoint receives username and password as form-data, validates credentials and issues a JWT.
    """

    # use username and password to authenticate user from local identity provider and get token
    access_token = await authenticate_local_user(
        credentials.username, credentials.password
    )

    if access_token:
        return JWTResponse(access_token=access_token)

    # Invalid username or password
    # wait a little to avoid brute force attacks
    await asyncio.sleep(1)
    raise HTTPException(status_code=403, detail={"error": "Invalid Credentials"})


async def authenticate_local_user(username: str, password: str) -> str | None:
    # authenticate local user credentials

    # brutal search over users, which are stored in a simple JSON list.
    # waiting to have graph in core to store them properly
    # TODOAUTH: get rid of this shameful loop
    users = get_users()
    for id, user in users.items():
        if user["username"] == username and user["password"] == password:
            # TODOAUTH: expiration with timezone needs to be tested
            # using seconds for easier testing
            expire_delta_in_seconds = float(get_env("CCAT_JWT_EXPIRE_MINUTES")) * 60
            expire = datetime.now(utc) + timedelta(seconds=expire_delta_in_seconds)
            # TODOAUTH: add issuer and redirect_uri (and verify them when a token is validated)
            return jwt.encode(
                dict(exp=expire, username=username),
                get_env("CCAT_JWT_SECRET"),
                algorithm=get_env("CCAT_JWT_ALGORITHM"),
            )
    return None