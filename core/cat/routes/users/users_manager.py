

from pytz import utc
import asyncio
from urllib.parse import urlencode
from datetime import datetime, timedelta
import jwt
from pydantic import BaseModel

from fastapi import APIRouter, Request, HTTPException, Response, status, Query, Depends
from fastapi.responses import RedirectResponse

from cat.env import get_env
from cat.auth.headers import frontend_auth
from cat.looking_glass.stray_cat import StrayCat
from cat.routes.static.templates import get_jinja_templates


router = APIRouter()


@router.get("/")
async def users_manager_page(
    request: Request,
    stray: StrayCat = Depends(frontend_auth)
):
    """Create, update and delete users and their permissions"""

    
    templates = get_jinja_templates()
    template_context = {}
    return templates.TemplateResponse(
        request=request, name="users/manager.html", context=template_context
    )
