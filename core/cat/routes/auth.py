
from typing import Dict
import asyncio
from cat.env import get_env
from pydantic import BaseModel

from fastapi import APIRouter, Request, HTTPException, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import datetime, timedelta
import jwt

#from cat.auth.jwt import create_access_token
from cat.factory.custom_auth_handler import BaseAuthHandler

from cat.log import log

router = APIRouter()

class UserCredentials(BaseModel):
    user_name: str
    password: str

class JWTResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

async def authenticate_local_user(username: str, password: str) -> str | None:
    # authenticate local user credentials

    # check credentials
    # TODOAUTH: where do we store admin user and pass?
    if username == "admin" and password == "admin":
        expire = datetime.utcnow() + timedelta(minutes=get_env("CCAT_JWT_EXPIRE_MINUTES"))
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

@router.post("/core_login_token")
async def core_login_token(request: Request, response: Response):

    # get form data from submitted core login form (/auth/core_login)
    form_data = await request.form()

    # use username and password to authenticate user from local identity provider and get token
    access_token = await authenticate_local_user(form_data["username"], form_data["password"])

    if access_token:
        response = RedirectResponse(url='/admin', status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="ccat_user_token", value=access_token)
        return response
    
    # credentials are wrong, wait a second (for brute force attacks) and then reply with error
    await asyncio.sleep(1)
    raise HTTPException(
            status_code=401,
            detail={
                "error": f"Invalid Credentials"
            }
        )


# TODOAUTH to define core login flow
@router.get("/core_login")
async def auth_index(request: Request):
    """Core login form, used when no external Identity Provider is configured"""

    return HTMLResponse("""
<form action="/auth/core_login_token" method="POST">
    <h1>^._.^</h1>
    <h3>Enjoy this top notch login form design.</h3>
    <div>
        <label for="username">Username:</label>
        <input type="text" id="username" name="username" required>
    </div>
    <div>
        <label for="password">Password:</label>
        <input type="password" id="password" name="password" required>
    </div>
    <div>
        <button type="submit">Login</button>
    </div>
</form>
""")


# TODOAUTH /logout endpoint

@router.post("/token")
async def auth_token(request: Request):
    """Endpoint called from client to authenticate user from local identity provider.
    """
    
    # get form data from submitted core login form (/auth/core_login)
    form_data = await request.form()

    # use username and password to authenticate user from local identity provider and get token
    access_token = await authenticate_local_user(form_data["username"], form_data["password"])

    if access_token:
         return JWTResponse(access_token=access_token)
    
    # Invalid username or password
    raise HTTPException(status_code=403, detail="Invalid username or password")


