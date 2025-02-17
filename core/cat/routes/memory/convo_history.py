

from typing import Dict
from fastapi import Request, APIRouter

from cat.auth.permissions import AuthPermission, AuthResource, check_permissions
from cat.looking_glass.stray_cat import StrayCat


router = APIRouter()


# DELETE conversation history from working memory
@router.delete("/conversation_history")
async def wipe_conversation_history(
    request: Request,
    cat: StrayCat = check_permissions(AuthResource.MEMORY, AuthPermission.DELETE),
) -> Dict:
    """Delete the specified user's conversation history from working memory"""

    cat.working_memory.history = []

    return {
        "deleted": True,
    }


# GET conversation history from working memory
@router.get("/conversation_history")
async def get_conversation_history(
    request: Request,
    cat: StrayCat = check_permissions(AuthResource.MEMORY, AuthPermission.READ),
) -> Dict:
    """Get the specified user's conversation history from working memory"""

    return {"history": cat.working_memory.history}


