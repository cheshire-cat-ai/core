from uuid import uuid5, NAMESPACE_DNS
from urllib.parse import urljoin
from typing import Dict

from cat import urls
from cat.env import get_env

from .base import Auth, User


class DefaultAuth(Auth):
    """Default auth handler, only admin user, based on environment variables."""

    slug = "default"
    name = "Default Auth handler"
    description = "Default auth handler, only admin user, based on environment variables."

    def get_admin(self) -> User:
        return User(
            id=uuid5(NAMESPACE_DNS, "admin"),
            name="admin",
            roles=["admin"],
        )

    async def authorize_user_from_jwt(
        self,
        token: str,
    ) -> User | None:
        payload = self.jwt.decode(token)
        if payload:
            return User(
                id=payload["sub"],
                name=payload["username"],
                roles=payload.get("roles", []),
            )

    async def authorize_user_from_key(
        self,
        key: str,
    ) -> User | None:
        env_key = get_env("CCAT_API_KEY")
        if (env_key is None) or (env_key == key):
            return self.get_admin()

    async def get_provider_login_url(
        self,
        redirect_uri: str
    ) -> str:
        return urljoin(
            urls.BASE_URL, f"/auth/internal-idp?redirect_uri={redirect_uri}"
        )

    async def authorize_user_from_oauth_code(
        self,
        redirect_uri: str,
        query_params: Dict
    ) -> User | None:
        # mock idp, not calling /token endpoint
        if query_params["code"] == "1":
            return
        return self.get_admin()
