from typing import Dict, List, Any
from uuid import UUID
from pydantic import BaseModel, field_validator

from cat.db import UserDB


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

    async def save_settings(self, settings: Dict) -> Dict:
        """
        Save user-specific settings.
        Will overwrite existing settings, so load existing settings first, update the dictionary, and then save.

        Parameters
        ----------
        settings : Dict
            The settings to store (must be JSON serialized).

        Returns
        -------
        Dict
            The saved settings.

        Examples
        --------
        >>> await user.save_settings({"theme": "dark"})
        {"theme": "dark"}
        """

        await UserDB.save(self.id, "settings", settings)
        return settings

    async def load_settings(self) -> Dict:
        """
        Load user-specific value by key.
        Returns an empty dict if no settings are found.

        Returns
        -------
        Dict
            The stored settings, or an empty dict if not found.
        Examples
        --------
        >>> await user.load_settings()
        {"theme": "dark"}
        """
        return await UserDB.load(self.id, "settings", {})