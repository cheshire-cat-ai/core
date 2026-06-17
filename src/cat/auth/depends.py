from fastapi import Depends, HTTPException

from cat.auth.user import User
from cat.context import ctx


def get_user(role: str | None = None) -> Depends:
    """
    Dependency that returns the current request's authenticated user.

    The user is authenticated once per request by the context middleware and
    stored in the request context. This dependency reads it and optionally
    enforces a role. Plugin endpoints can skip it entirely and read
    `from cat import user`; routes use it when they want explicit role gating.

    Parameters
    ----------
    role : str | None
        Role required for this route. None means just authenticated.

    Returns
    -------
    Depends
        Resolves to the authenticated User, or raises HTTPException(403).
    """

    def current_user() -> User:
        user = ctx().user
        if user is None:
            raise HTTPException(status_code=403, detail="Invalid Credentials")
        if role and not user.has_role(role):
            raise HTTPException(status_code=403, detail="Insufficient role")
        return user

    return Depends(current_user)
