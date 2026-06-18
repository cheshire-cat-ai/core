from .base import Auth


class DefaultAuth(Auth):
    """The bare fallback verifier — present only when no plugin provides its own.

    It adds nothing to `Auth`: it inherits core-signed-JWT verification and the
    master `API_KEY` → admin policy. It has no login flow (that lives in a
    plugin), so the moment a plugin registers an auth handler this default steps
    aside (see `CheshireCat.refresh_registry`). The master key keeps working
    because that logic lives in the `Auth` base, which every handler inherits.
    """

    slug = "default"
    name = "Default Auth handler"
    description = "Core auth handler: verifies core-signed JWTs and the master API key."
