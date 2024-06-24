
from typing import Dict
from pytz import utc
import asyncio
from urllib.parse import urlencode
from datetime import datetime, timedelta
import jwt
from pydantic import BaseModel

from fastapi import APIRouter, Request, HTTPException, Response, status, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates


#from cat.auth.jwt import create_access_token
from cat.env import get_env
from cat.factory.custom_auth_handler import BaseAuthHandler

from cat.log import log

router = APIRouter()

class UserCredentials(BaseModel):
    username: str
    password: str

class JWTResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

async def authenticate_local_user(username: str, password: str) -> str | None:
    # authenticate local user credentials

    # check credentials
    # TODOAUTH: where do we store admin user and pass?
    if username == "admin" and password == "admin":
        # TODOAUTH: expiration with timezone needs to be tested
        # using seconds for easier testing
        expire_delta_in_seconds = float(get_env("CCAT_JWT_EXPIRE_MINUTES")) * 60
        expire = datetime.now(utc) + timedelta(seconds=expire_delta_in_seconds)
        # TODOAUTH: add issuer and redirect_uri (and verify them when a token is validated)
        return jwt.encode(
            dict(
                exp=expire,
                username=username
            ),
            get_env("CCAT_JWT_SECRET"),
            algorithm=get_env("CCAT_JWT_ALGORITHM")
        )
    return None


# set cookies and redirect to admin page
@router.post("/redirect")
async def core_login_token(request: Request, response: Response):

    # get form data from submitted core login form (/auth/core_login)
    form_data = await request.form()

    # use username and password to authenticate user from local identity provider and get token
    access_token = await authenticate_local_user(form_data["username"], form_data["password"])

    if access_token:
        response = RedirectResponse(
            url=form_data["referer"],
            status_code=status.HTTP_303_SEE_OTHER
        )
        response.set_cookie(key="ccat_user_token", value=access_token)
        return response
    
    # credentials are wrong, wait a second (for brute force attacks) and go back to login
    await asyncio.sleep(1)
    referer_query = urlencode({
        "referer": form_data["referer"],
        "retry": 1,
    })
    login_url = f"/auth/login?{referer_query}"
    response = RedirectResponse(
        url=login_url,
        status_code=status.HTTP_303_SEE_OTHER
    )
    return response


# TODOAUTH to define core login flow
@router.get("/login")
async def auth_index(request: Request, referer: str = Query(None), retry: int = Query(0)):
    """Core login form, used when no external Identity Provider is configured"""

    error_message = ""
    if retry == 1:
        error_message = "Invalid Credentials"

    if referer is None:
        referer = "/admin/"

    template_context = {
        "referer": referer,
        "error_message": error_message
    }

    templates = Jinja2Templates(directory="cat/routes/static/core_static_folder/")
    return templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context=template_context
    )


# TODOAUTH /logout endpoint

@router.post("/token")
async def auth_token(credentials: UserCredentials):
    """Endpoint called from client to get a JWT from local identity provider.
        This endpoint receives username and password as form-data, validates credentials and issues a JWT.
    """

    # use username and password to authenticate user from local identity provider and get token
    access_token = await authenticate_local_user(credentials.username, credentials.password)

    if access_token:
         return JWTResponse(access_token=access_token)
    
    # Invalid username or password
    # wait a little to avoid brute force attacks
    await asyncio.sleep(1)
    raise HTTPException(
        status_code=403,
        detail={
            "error": f"Invalid Credentials"
        }
    )


