import asyncio
from typing import Dict, List, Annotated
from urllib.parse import urlencode
from pydantic import BaseModel

from fastapi import APIRouter, Request, HTTPException, Response, status, Query, Form
from fastapi.responses import RedirectResponse

from cat.db import crud
from cat.looking_glass.stray_cat import StrayCat
from cat.auth.permissions import AuthPermission, AuthResource, get_full_permissions, check_permissions
from cat.routes.static.templates import get_jinja_templates

router = APIRouter()

class UserCredentials(BaseModel):
    username: str
    password: str

class JWTResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# TODOAUTH /logout endpoint
# TODOAUTH /token/refresh

@router.post("/token", response_model=JWTResponse)
async def auth_token(request: Request, credentials: UserCredentials):
    """Endpoint called from client to get a JWT from local identity provider.
    This endpoint receives username and password as form-data, validates credentials and issues a JWT.
    """

    # use username and password to authenticate user from local identity provider and get token
    auth_handler = request.app.state.ccat.core_auth_handler
    access_token = auth_handler.issue_jwt(
        credentials.username, credentials.password
    )

    if access_token:
        return JWTResponse(access_token=access_token)

    # Invalid username or password
    # wait a little to avoid brute force attacks
    await asyncio.sleep(1)
    raise HTTPException(status_code=403, detail={"error": "Invalid Credentials"})


# login HTML form GET
@router.get("/login", include_in_schema=False)
async def auth_login_form_get(
    request: Request, referer: str = Query(None), retry: int = Query(0)
):
    """Core login form"""

    error_message = ""
    if retry == 1:
        error_message = "Invalid Credentials"

    if referer is None:
        referer = "/admin/"

    templates = get_jinja_templates()
    template_context = {
        "referer": referer,
        "error_message": error_message,
        "show_default_passwords": len(crud.get_users().keys()) == 2,
    }

    response = templates.TemplateResponse(
        request=request, name="auth/login.html", context=template_context
    )
    response.delete_cookie(key="ccat_user_token")
    return response


# login HTML form POST. Set cookies and redirect to origin page after login
@router.post("/login", include_in_schema=False)
async def auth_login_form_post(
    request: Request,
    response: Response,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    referer: Annotated[str, Form()]
):

    # use username and password to authenticate user from local identity provider and get token
    auth_handler = request.app.state.ccat.core_auth_handler
    access_token = auth_handler.issue_jwt(
        username, password
    )

    # right credentials, set cookie and redirect to referer
    if access_token:
        response = RedirectResponse(
            url=referer, status_code=status.HTTP_303_SEE_OTHER
        )
        response.set_cookie(key="ccat_user_token", value=access_token)
        return response

    # credentials are wrong, wait a second (for brute force attacks) and go back to login
    await asyncio.sleep(1)
    referer_query = urlencode(
        {
            "referer": referer,
            "retry": 1,
        }
    )
    login_url = f"/auth/login?{referer_query}"
    response = RedirectResponse(url=login_url, status_code=status.HTTP_303_SEE_OTHER)
    return response


@router.get("/available-permissions", response_model=Dict[AuthResource, List[AuthPermission]])
async def get_available_permissions(
    cat: StrayCat = check_permissions(AuthResource.USERS, AuthPermission.LIST),
):
    """Returns all available resources and permissions."""
    return get_full_permissions()

