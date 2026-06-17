from fastapi import APIRouter

from cat.auth import get_user, User

router = APIRouter(prefix="/me", tags=["User"])

@router.get("")
async def get_user_info(
    user: User = get_user(),
) -> User:
    """Returns user information."""
    return user
