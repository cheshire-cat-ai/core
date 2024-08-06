


from fastapi import APIRouter, Request, Depends

from cat.auth.permissions import AuthResource, AuthPermission
from cat.auth.connection import CoreFrontendAuth
from cat.looking_glass.stray_cat import StrayCat
from cat.routes.static.templates import get_jinja_templates


router = APIRouter()


@router.get("/", include_in_schema=False)
async def users_manager_page(
    request: Request,
    stray: StrayCat = Depends(
        CoreFrontendAuth(AuthResource.USERS, AuthPermission.WRITE)
    )
):
    """Create, update and delete users and their permissions"""

    templates = get_jinja_templates()
    template_context = {}
    return templates.TemplateResponse(
        request=request, name="users/manager.html", context=template_context
    )
