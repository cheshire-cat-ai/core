"""
The ambient access layer — how code reaches cross-cutting behaviour and state
without threading objects around.

Three submodules, one idea:

- `verbs`        — the actions you *call*: `llm`, `embedder`, `hook`,
                   `execute_hook`, `agui_event`, `call_agent`, `auth`, `get`.
- `context_vars` — per-request state (a `contextvars.ContextVar`): `ctx`, `user`.
- `runtime`      — the one `CheshireCat` per process: `ccat`, `plugin`.

Everything is reached through the `cat` front door (`from cat import llm, user,
hook`). The submodules are addressed directly only by framework internals.
"""

from cat.ambient.verbs import (
    send_json,
    agui_event,
    llm,
    embedder,
    auth,
    hook,
    execute_hook,
    get,
    call_agent,
)

__all__ = [
    "send_json",
    "agui_event",
    "llm",
    "embedder",
    "auth",
    "hook",
    "execute_hook",
    "get",
    "call_agent",
]
