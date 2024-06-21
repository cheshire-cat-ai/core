
from typing import Dict
from pytz import utc
import asyncio
from urllib.parse import urlencode
from datetime import datetime, timedelta
import jwt
from pydantic import BaseModel

from fastapi import APIRouter, Request, HTTPException, Response, status, Query
from fastapi.responses import HTMLResponse, RedirectResponse

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
        expire = datetime.now(utc) + timedelta(minutes=get_env("CCAT_JWT_EXPIRE_MINUTES"))
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
    referer_query = urlencode({"referer": form_data["referer"]})
    login_url = f"/auth/login?{referer_query}"
    response = RedirectResponse(
        url=login_url,
        status_code=status.HTTP_303_SEE_OTHER
    )
    return response


# TODOAUTH to define core login flow
@router.get("/login")
async def auth_index(request: Request, referer: str = Query(None)):
    """Core login form, used when no external Identity Provider is configured"""

    return HTMLResponse(f"""                   
<form action="/auth/redirect" method="POST">
    <h1>^._.^</h1>
    <h3>Enjoy this top notch login form design.</h3>
    <div>
        <input type="text" id="username" name="username" required placeholder="Username">
    </div>
    <div>
        <input type="password" id="password" name="password" required placeholder="Password">
    </div>
    <div>
        <input type="hidden" name="referer" value="{referer}">
    </div>
    <div>
        <button type="submit">Login</button>
    </div>
</form>
    """)


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


