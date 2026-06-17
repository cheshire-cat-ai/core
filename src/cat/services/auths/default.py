from uuid import uuid5, NAMESPACE_DNS
from urllib.parse import urljoin
from typing import Dict

from fastapi import Request

from cat import config

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

    async def authenticate(self, request: Request) -> User | None:
        # No API key configured: everything is open, grant admin to all.
        if config.API_KEY is None:
            return self.get_admin()
        return await super().authenticate(request)

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
        api_key = config.API_KEY
        if (api_key is None) or (api_key == key):
            return self.get_admin()

    async def get_provider_login_url(
        self,
        redirect_uri: str
    ) -> str:
        return urljoin(
            config.URL, f"/auth/internal-idp?redirect_uri={redirect_uri}"
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
