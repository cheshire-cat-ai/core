from abc import ABC, abstractmethod
from typing import Dict

from fastapi import Request

from cat.auth.jwt import JWTHelper
from cat.auth.user import User
from cat import log

from ..service import SingletonService


class Auth(ABC, SingletonService):
    """
    Base class to build custom Auth systems.
    """

    service_type = "auths"

    jwt = JWTHelper()

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

    @abstractmethod
    async def authorize_user_from_jwt(
        self,
        token: str,
    ) -> User | None:
        pass

    @abstractmethod
    async def authorize_user_from_key(
        self,
        api_key: str,
    ) -> User | None:
        pass

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
