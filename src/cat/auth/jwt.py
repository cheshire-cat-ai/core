from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError

from cat.auth.user import User
from cat.env import get_env
from cat import log


class JWTHelper:
    """JWT utility for encoding, decoding, and detecting JWTs."""

    def is_jwt(self, token: str) -> bool:
        try:
            jwt.decode(token, options={"verify_signature": False})
            return True
        except InvalidTokenError:
            return False

    def encode(self, user: User) -> str:
        expire_delta_in_seconds = float(get_env("CCAT_JWT_EXPIRE_MINUTES")) * 60
        expires = datetime.now(timezone.utc) + timedelta(seconds=expire_delta_in_seconds)

        jwt_content = {
            "sub": str(user.id),
            "username": user.name,
            "roles": user.roles,
            "custom": user.custom,
            "exp": expires,
        }
        return jwt.encode(
            jwt_content,
            get_env("CCAT_JWT_SECRET"),
            algorithm="HS256",
        )

    def decode(self, token: str) -> dict | None:
        """Decode JWT. Returns None if unable to decode or signature is wrong."""
        try:
            return jwt.decode(
                token,
                get_env("CCAT_JWT_SECRET"),
                algorithms=["HS256"],
            )
        except Exception:
            log.warning("Could not decode JWT")
            return None
