from fastapi import Depends, HTTPException

from cat.auth.user import User
from cat.context import ctx


# Reserved role value meaning "any authenticated user, regardless of roles".
# Cannot be used as a real role name.
AUTHENTICATED = "authenticated"


def _get_user(role: "str | list[str] | None" = None) -> Depends:
    """
    Internal routes auth dependency. **Not for plugins.**

    This is a raw FastAPI `Depends` used only by core routes under `cat.routes`,
    which are plain `APIRouter`s and want explicit, FastAPI-native role gating.

    Plugins get the same thing as *sugar* instead:

        from cat import user                 # read the authenticated user

        @endpoint.get("/admin/stuff", role="admin")   # gate by role
        async def stuff():
            return {"hi": user.name}

    Both paths share one source of truth: the user is authenticated once per
    request by the context middleware and stored in the request context; this
    dependency just reads it and optionally enforces a role. The `role=` kwarg on
    `@endpoint` injects exactly this dependency under the hood.

    Parameters
    ----------
    role : str | list[str] | None
        - None or "authenticated": any logged-in user (no specific role).
        - "admin": must have that role.
        - ["a", "b"]: must have *any* of these (OR). Empty list = any logged-in.

    Returns
    -------
    Depends
        Resolves to the authenticated User, or raises HTTPException(403).
    """

    # Normalise to the list of acceptable roles (empty == auth-only).
    if role is None or role == AUTHENTICATED:
        required: list[str] = []
    elif isinstance(role, str):
        required = [role]
    else:
        required = list(role)

    def current_user() -> User:
        user = ctx().user
        if user is None:
            raise HTTPException(status_code=403, detail="Invalid Credentials")
        if required and not user.has_role(*required):
            raise HTTPException(status_code=403, detail="Insufficient role")
        return user

    return Depends(current_user)
