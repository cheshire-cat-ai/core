from typing import Dict

from fastapi import (
    Depends,
    Request,
    APIRouter,
)

from cat.auth.connection import HTTPAuth
from cat.auth.permissions import AuthPermission, AuthResource

router = APIRouter()

@router.post("/")
async def chat(
    request: Request,
    stray=Depends(HTTPAuth(AuthResource.CONVERSATION, AuthPermission.WRITE)),
) -> Dict:
    """REST chat interaction with the Cat (no intermediate tokens)"""
    user_message = await request.json()
    user_message["user_id"] = stray.user_id
    response = await stray.__call__(user_message)
    return {
        "user_id": response.user_id,
        "type": response.type,
        "content": response.content,
        "why": response.why
    }
