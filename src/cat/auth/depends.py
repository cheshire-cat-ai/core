from typing import TYPE_CHECKING

from fastapi import Depends, Request, HTTPException
from fastapi.security.api_key import APIKeyHeader

from cat.auth.user import User

if TYPE_CHECKING:
    from cat.looking_glass.cheshire_cat import CheshireCat


def get_user(role: str | None = None) -> Depends:
    """
    Dependency that authenticates the user and optionally checks role.

    Loops through auth handlers calling `auth.authenticate(request)`.
    First User returned wins. Then checks `user.has_role(role)` if provided.

    Parameters
    ----------
    role : str | None
        Role required for this route.
        None means just authenticated (no role check).

    Returns
    -------
    Depends
        Dependency that resolves to the authenticated User.
        Raises HTTPException(403) if auth fails or role insufficient.

    Usage
    -----
    @router.get("/agents")
    async def list_agents(user: User = get_user()):
        pass

    @router.put("/settings/{id}")
    async def update_settings(user: User = get_user(role="admin")):
        pass
    """

    async def authenticate_and_check(
        request: Request,
        credential: str | None = Depends(APIKeyHeader(
            name="Authorization",
            description="Insert here your CCAT_API_KEY, or Bearer JWT token.",
            auto_error=False,
        )),
    ) -> User:
        ccat = request.app.state.ccat
        auth_handlers = await ccat.get_all("auths")

        for ah in auth_handlers.values():
            user = await ah.authenticate(request)
            if user and isinstance(user, User):
                if role and not user.has_role(role):
                    raise HTTPException(
                        status_code=403,
                        detail="Insufficient role",
                    )
                request.state.user = user
                return user

        raise HTTPException(status_code=403, detail="Invalid Credentials")

    return Depends(authenticate_and_check)


def get_ccat() -> Depends:
    """
    Dependency helper to get CheshireCat instance from request.

    Returns
    -------
    Depends
        Dependency that resolves to the CheshireCat instance.

    Usage
    -----
    @router.get("/status")
    async def status(ccat = get_ccat()):
        # ccat is the CheshireCat instance
        pass
    """
    def extract_ccat(request: Request) -> "CheshireCat":
        return request.app.state.ccat
    return Depends(extract_ccat)
