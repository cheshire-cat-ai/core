
from typing import Dict
import asyncio
from cat.env import get_env
from pydantic import BaseModel

from fastapi import APIRouter, Depends, Request, Body, Query, HTTPException
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

"""
@router.post("/token")
async def get_access_token(creds: UserCredentials):

    # TODOAUTH: have credentials in DB
    if creds.user_name == "admin" and creds.password == "admin":
        access_token = create_access_token({
            "sub": creds.user_name
        })
        return JWTResponse(access_token=access_token)
    
    # credentials are wrong, wait a second (for brute force attacks) and then reply with error
    await asyncio.sleep(1)
    raise HTTPException(
            status_code=401,
            detail={
                "error": f"Invalid Credentials"
            }
        )
"""



#from fastapi import Depends
#from fastapi.security import OAuth2AuthorizationCodeBearer

#oauth2_scheme = OAuth2AuthorizationCodeBearer(
    # ???
#    authorizationUrl="http://localhost:8080/realms/gatto/protocol/openid-connect/auth",
    # The URL to obtain the OAuth2 token
#    tokenUrl="http://localhost:8080/realms/gatto/protocol/openid-connect/token",
    # Where to obtain a new token
#    refreshUrl="",
#    scheme_name="OAuth2 for da Cat",
#    auto_error=True,
#)


#async def get_stray(token: str = Depends(auth_handler.oauth2_scheme)):
    # if token is None, it means that the Authorization header is not present
    # otherwise you get the token itself
#    log.warning(token)
#    return {"user": 42}

#@router.get("")
#async def prova(stray: dict = Depends(get_stray)):
#    return stray


@router.get("/core_login")
async def auth_index(request: Request):
    """Core login form, used when no external Identity Provider is configured"""

    return HTMLResponse("""
<form action="/auth/token" method="POST">
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


@router.get("/login")
async def auth_login(request: Request):
    """Send request to the Identity Provider login endpoint"""

    auth_handler: BaseAuthHandler = request.app.state.ccat.auth_handler

    # Redirect the browser to the identity provider's authorization page
    return RedirectResponse(
        url = '/auth/core_login'
    )

# TODOAUTH /logout endpoint

@router.post("/token")
async def auth_token(request: Request):
    """Endpoint called from client to authenticate user from local identity provider.
    """

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
    
    # get form data from submitted core login form (/auth/core_login)
    form_data = await request.form()

    # use username and password to authenticate user from local identity provider and get token
    access_token = await authenticate_local_user(form_data["username"], form_data["password"])

    if access_token:
        return {
            "token": access_token
        }
    
    # Invalid username or password
    raise HTTPException(status_code=403, detail="Invalid username or password")


