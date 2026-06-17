import os
import hashlib

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Form

from cat import paths
from cat.env import get_env

router = APIRouter(prefix="/auth/internal-idp", tags=["Default IDP"])

# TODOV2: internal idp should give a 403 when default auth handler is not active

@router.get("", include_in_schema=False
)
async def internal_idp(redirect_uri: str) -> HTMLResponse:
    html_path = os.path.join( paths.BASE_PATH, "routes/auth/default_idp/idp.html" )
    with open(html_path, "r") as f:
        html = f.read()
    html = html.replace("{{redirect_uri}}", redirect_uri)
    return HTMLResponse(html)


@router.post("/login", include_in_schema=False)
async def internal_idp_login(
    api_key: str = Form(...),
    redirect_uri: str = Form(...)
):
    if api_key == get_env("CCAT_API_KEY"):
        code = hashlib.sha256(api_key.encode()).hexdigest()[:16]
        return RedirectResponse(
            url=f"{redirect_uri}?code={code}",
            status_code=303
        )
    return RedirectResponse(
        url=f"/auth/internal-idp?redirect_uri={redirect_uri}",
        status_code=303
    )
