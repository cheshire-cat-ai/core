"""The Simple OAuth handler.

A full `Auth` subclass: it inherits JWT + API-key *verification* from the base
(so the Cat already trusts the sessions it mints) and adds the *login* half — an
OAuth dance against the built-in mock identity provider in `endpoints.py`.

This is the reference a real SSO plugin is cloned from: keep the two methods
below, point them at Google / Auth0 / your IdP, and you are in production. Core
never changes — it only ever verifies the JWT this flow produces.
"""

from uuid import uuid5, NAMESPACE_DNS
from urllib.parse import urljoin
from typing import Dict

from cat import config, User
from cat.base import Auth


class SimpleOAuth(Auth):
    """Example OAuth login against a built-in mock IdP. Replace for production."""

    slug = "simple"
    name = "Simple OAuth"
    description = "Example OAuth login flow against a built-in mock identity provider."

    def get_admin(self) -> User:
        return User(
            id=uuid5(NAMESPACE_DNS, "admin"),
            name="admin",
            roles=["admin"],
        )

    async def get_provider_login_url(self, redirect_uri: str) -> str:
        """Where to send the browser to start the login — here, the mock IdP page.
        A real handler returns its provider's authorize URL."""
        return urljoin(config.URL, f"/auth/internal-idp?redirect_uri={redirect_uri}")

    async def authorize_user_from_oauth_code(
        self,
        redirect_uri: str,
        query_params: Dict,
    ) -> User | None:
        """Exchange the provider's `code` for a User. The mock IdP only emits a
        code once the API key matched, so any code present authorizes admin.
        A real handler calls the provider's token endpoint here."""
        if query_params.get("code"):
            return self.get_admin()
        return None
