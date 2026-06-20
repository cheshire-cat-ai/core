"""
Per-request ambient context, stored in a `contextvars.ContextVar`.

Set once per request by the middleware in `cat.startup`; each asyncio Task gets
its own copy, so concurrent requests never see each other's user or stream
callback. Importing builds nothing — `ctx()` resolves the current request lazily.

`from cat import user` binds a live proxy that resolves the current request's
user on every access. The process-wide CheshireCat handle lives in `cat.ambient.runtime`.
"""

from contextlib import contextmanager
from contextvars import ContextVar, Token
from dataclasses import dataclass
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import Request
    from cat.auth.user import User


@dataclass
class Ctx:
    """Per-request ambient state. Mutable: the stream callback is attached
    after authentication, once the connection is ready to receive events."""

    user: "User | None"
    request: "Request | None" = None
    stream: Callable | None = None
    # working_memory intentionally omitted — out of scope for this change.


_ctx: ContextVar["Ctx | None"] = ContextVar("cat_ctx", default=None)


def ctx() -> Ctx:
    """Return the current request context, or raise if outside a request."""
    c = _ctx.get()
    if c is None:
        raise RuntimeError(
            "Outside a request — no user/stream available. "
            "Capabilities that read the request context (e.g. `user`) must be "
            "called inside a handler, tool, or agent, never at import time."
        )
    return c


def set_ctx(c: Ctx) -> Token:
    """Set the request context, returning a token to reset it."""
    return _ctx.set(c)


def reset_ctx(token: Token) -> None:
    """Restore the previous request context."""
    _ctx.reset(token)


@contextmanager
def use_ctx(c: Ctx):
    """Enter a request context for the duration of a block (set + reset)."""
    token = _ctx.set(c)
    try:
        yield c
    finally:
        _ctx.reset(token)


class _UserProxy:
    """Live proxy to the current request's user.

    `from cat import user` binds this once; every attribute read resolves the
    user of whatever request is currently on the event loop. Reading it outside
    a request raises a clear error rather than returning shared/stale state.
    """

    def _user(self) -> "User":
        user = ctx().user
        if user is None:
            raise RuntimeError(
                "No authenticated user in the current request context."
            )
        return user

    def __getattr__(self, name):
        return getattr(self._user(), name)

    def __repr__(self):
        c = _ctx.get()
        if c is None or c.user is None:
            return "<cat.user (no active request)>"
        return f"<cat.user {c.user!r}>"


user = _UserProxy()
