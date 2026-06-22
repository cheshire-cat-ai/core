from typing import List, Any
from uuid import UUID
from pydantic import BaseModel, field_validator

from cat.db import UserStore


class User(BaseModel):
    """
    Class to represent a User.
    Will be created by Auth handler(s) starting from a credential (jwt or key).
    Instance of the authenticated user is stored under request.state.user and is available in request services.
    Will be accessible in services via `Service.user`
    """

    id: UUID
    name: str

    # roles as flat string list (e.g. ["admin", "user", "editor"])
    # "admin" role passes all role checks
    roles: List[str] = []

    # only put in here what you are comfortable to pass plugins:
    # - profile data
    # - custom attributes
    custom: Any = {}

    @field_validator("id", mode="before")
    def ensure_uuid(cls, v):
        """
        Accept either a uuid.UUID or a UUID string; normalize to uuid.UUID.
        """
        if isinstance(v, UUID):
            return v
        try:
            return UUID(str(v))
        except Exception:
            raise ValueError("User id must be a valid UUID or UUID string")

    def has_role(self, *required: str) -> bool:
        """
        Check if user has any of the required roles (OR logic).
        The ``"admin"`` role passes all role checks.

        Returns
        -------
        bool
            Whether the user has at least one of the required roles.

        Examples
        --------
        >>> user.has_role("admin", "editor")
        True
        """
        if "admin" in self.roles:
            return True
        return any(r in self.roles for r in required)

    def is_admin(self) -> bool:
        """
        Check if user has the admin role.

        Returns
        -------
        bool
            Whether the user is an admin.
        """
        return "admin" in self.roles

    async def save(self, key: str, value: Any) -> Any:
        """
        Save a value scoped to this user, under `key` (full replacement).

        The data lives in a per-user key-value store, so two users never see
        each other's data. To update a collection, load it, change it, save it
        back.

        Parameters
        ----------
        key : str
            The key to store the value under.
        value : Any
            Any JSON-serializable value.

        Returns
        -------
        Any
            The saved value.

        Examples
        --------
        >>> await user.save("todos", [{"text": "buy milk", "done": False}])
        [{"text": "buy milk", "done": False}]
        """
        return await UserStore.save(self.id, key, value)

    async def load(self, key: str, default: Any = None) -> Any:
        """
        Load a value scoped to this user. Returns `default` if the key is unset.

        Parameters
        ----------
        key : str
            The key to read.
        default : Any
            Value to return if the key is not found.

        Returns
        -------
        Any
            The stored value, or `default`.

        Examples
        --------
        >>> await user.load("todos", [])
        [{"text": "buy milk", "done": False}]
        """
        return await UserStore.load(self.id, key, default)

    async def delete(self, key: str) -> bool:
        """
        Delete a user-scoped key.

        Parameters
        ----------
        key : str
            The key to delete.

        Returns
        -------
        bool
            True if a value was removed, False if the key was unset.
        """
        return await UserStore.delete(self.id, key)