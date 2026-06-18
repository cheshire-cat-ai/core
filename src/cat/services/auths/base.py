from abc import ABC
from typing import Dict
from uuid import uuid5, NAMESPACE_DNS

from fastapi import Request

from cat.auth.jwt import JWTHelper
from cat.auth.user import User

from ..service import Service


class Auth(ABC, Service):
    """
    Base class to build custom Auth systems.

    Out of the box a handler is a complete verifier: it extracts the credential
    from the request, trusts any core-signed JWT (`authorize_user_from_jwt`), and
    accepts the master API key (`authorize_user_from_key` → the admin user). Every
    method is overridable, so subclasses typically only add a *login* flow —
    override `get_provider_login_url` + `authorize_user_from_oauth_code` to mint
    those JWTs from an OAuth provider — or change the key/identity policy by
    overriding `authorize_user_from_key` / `get_admin`.

    Because verification lives here, the core `DefaultAuth` is just this base with
    a slug, and can step aside the moment a plugin registers its own handler.
    """

    service_type = "auths"

    jwt = JWTHelper()

    def get_admin(self) -> User:
        """The user the master API key maps to. Override to change identity/roles."""
        return User(
            id=uuid5(NAMESPACE_DNS, "admin"),
            name="admin",
            roles=["admin"],
        )

    def get_credential(self, request: Request) -> str | None:
        """Extract credential from request.
        Override for custom credential sources.

        Default: Authorization header (strip "Bearer ") → access_token cookie (HTTP)
        """

        # HTTP request
        auth_header = request.headers.get("Authorization")
        if auth_header:
            return auth_header.replace("Bearer ", "")

        # Fallback to cookie
        return request.cookies.get("access_token")

    async def authenticate(self, request: Request) -> User | None:
        """Main entry point for authentication.
        Override for full control over the authentication flow.

        Default: get_credential() → authorize_user_from_credential()
        """
        credential = self.get_credential(request)
        if credential is None:
            return None
        return await self.authorize_user_from_credential(credential)

    async def authorize_user_from_credential(
        self,
        credential: str,
    ) -> User | None:
        if self.jwt.is_jwt(credential):
            return await self.authorize_user_from_jwt(credential)
        else:
            return await self.authorize_user_from_key(credential)

    async def authorize_user_from_jwt(
        self,
        token: str,
    ) -> User | None:
        """Verify a core-signed JWT and rebuild the User from its claims.

        Generic to every handler: the Cat trusts the sessions any login flow
        mints with `self.jwt.encode(user)`. Override only for non-core tokens
        (e.g. verifying a third-party JWT against a JWKS).
        """
        payload = self.jwt.decode(token)
        if not payload:
            return None
        return User(
            id=payload["sub"],
            name=payload["username"],
            roles=payload.get("roles", []),
        )

    async def authorize_user_from_key(
        self,
        api_key: str,
    ) -> User | None:
        """Authorize from the master API key (→ the admin user).

        This is the simplest possible key policy. Override for custom schemes,
        e.g. per-user keys looked up in a database.
        """
        from cat import config

        if config.API_KEY is not None and api_key == config.API_KEY:
            return self.get_admin()
        return None

    async def get_provider_login_url(
        self,
        redirect_uri: str
    ) -> str:
        """Return the OAuth provider login URL.
        Implement this method to have your Auth handler support OAuth.
        """
        raise Exception(
            "To support OAuth, auth handlers must implement " +
            "`get_provider_login_url` and `authorize_user_from_oauth_code`"
        )

    async def authorize_user_from_oauth_code(
        self,
        redirect_uri: str,
        query_params: Dict
    ) -> User | None:
        """
        Exchange OAuth provider code/state for user info and map it to internal User.
        Implement this method to have your Auth handler support OAuth.
        """
        raise Exception(
            "To support OAuth, auth handlers must implement " +
            "`get_provider_login_url` and `authorize_user_from_oauth_code`"
        )
