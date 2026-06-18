from fastapi import APIRouter

from cat.auth import User
from cat.auth.depends import _get_user

router = APIRouter(prefix="/me", tags=["User"])

@router.get("")
async def get_user_info(
    user: User = _get_user(),
) -> User:
    """Returns user information."""
    return user
