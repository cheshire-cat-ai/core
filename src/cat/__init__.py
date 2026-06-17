"""
The `cat` package — the one import surface.

`cat` means exactly one thing: this package. There is no userspace `cat`
instance to thread around. You don't import capabilities and hold them; you
import *names* whose behaviour is resolved, per call, against the configured
installation:

    from cat import llm, embedder, memory, auth, hook, user

Plus the building blocks for plugins (`Agent`, `tool`, `endpoint`, `config`,
`log`) and a rarely-needed registry escape hatch (`get`, `call_agent`).
"""

from .config import config
from .log import log
from .mad_hatter.decorators import tool, endpoint
from .services.service import Service
from .services.agents.base import Agent
from .auth import User

# Ambient request context
from .context import user

# Ambient capabilities (functions resolved lazily at call time)
from .capabilities import (
    llm,
    embedder,
    memory,
    auth,
    hook,
    get,
    call_agent,
)

__all__ = [
    # building blocks
    "config",
    "log",
    "tool",
    "endpoint",
    "Service",
    "Agent",
    "User",
    # ambient context
    "user",
    # ambient capabilities
    "llm",
    "embedder",
    "memory",
    "auth",
    "hook",
    "get",
    "call_agent",
]
