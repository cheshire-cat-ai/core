"""
Ambient request context and the single CheshireCat handle.

Two ambient things live here, both reached lazily so importing this module
builds nothing:

- `ctx()` / `user` — per-request state stored in a `contextvars.ContextVar`,
  set once per request by the middleware in `cat.startup`. Each asyncio Task
  gets its own copy, so concurrent requests never see each other's user or
  stream callback. `from cat import user` binds a live proxy that resolves the
  current request's user on every access.

- `ccat()` — the one `CheshireCat` instance per process. It is internal plumbing
  behind the `cat` package front door; user-facing code never names it. Named for
  the `ccat_*` DB tables and the historical nickname; pairs with `ctx()` as the
  two short ambient accessors. ("app" means the FastAPI app, nothing else.)
"""

from contextlib import contextmanager
from contextvars import ContextVar, Token
from dataclasses import dataclass
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import Request
    from cat.auth.user import User
    from cat.looking_glass.cheshire_cat import CheshireCat


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


class _PluginProxy:
    """Live proxy to the plugin that owns the calling code.

    `from cat import plugin` binds this once; every attribute read resolves the
    plugin of whatever code is currently executing (matched by call-stack file
    path). Lets plugin code reach its own metadata/path — `plugin.path` — without
    importing the app handle or threading `self`.
    """

    def _plugin(self):
        return ccat().plugin

    def __getattr__(self, name):
        return getattr(self._plugin(), name)

    def __repr__(self):
        return "<cat.plugin (current)>"


plugin = _PluginProxy()


# ---------------------------------------------------------------------------
# The single CheshireCat instance per process.
# ---------------------------------------------------------------------------

_ccat: "CheshireCat | None" = None


def ccat() -> "CheshireCat":
    """Return the one CheshireCat instance. Internal usage only."""
    if _ccat is None:
        raise RuntimeError("CheshireCat is not bootstrapped yet.")
    return _ccat


def set_ccat(instance: "CheshireCat") -> None:
    """Register the process-wide CheshireCat instance (called at bootstrap)."""
    global _ccat
    _ccat = instance
