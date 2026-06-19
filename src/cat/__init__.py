"""
The `cat` package — the one import surface.

`cat` means exactly one thing: this package. There is no userspace `cat`
instance to thread around. You don't import capabilities and hold them; you
import *names* whose behaviour is resolved, per call, against the configured
installation:

    from cat import log, tool, endpoint, hook, config, user, llm

Plus model/agent building blocks (`embedder`, `Agent`) and the advanced tier:
base classes (`Service`, `User`) and the registry escape hatch (`get`,
`call_agent`). Names are ordered here by how often plugins actually reach for
them, most-used first.
"""

# --- building blocks (most used) -------------------------------------------
# (config is imported before log because log reads it at construction time;
#  __all__ below is ordered by usage frequency, not import order.)
from .config import config
from .log import log
from .mad_hatter.decorators import tool, endpoint
from .capabilities import hook

# --- ambient request context -----------------------------------------------
from .context import user, plugin
from .capabilities import agui_event

# --- models & agents -------------------------------------------------------
from .capabilities import llm, embedder
from .services.agents.base import Agent
from .services.directives.base import Directive

# --- advanced: base classes & registry escape hatch ------------------------
from .services.service import Service
from .auth import User
from .capabilities import get, call_agent

__all__ = [
    # building blocks (most used)
    "log",
    "tool",
    "endpoint",
    "hook",
    "config",
    # ambient request context
    "user",
    "plugin",
    "agui_event",
    # models & agents
    "llm",
    "embedder",
    "Agent",
    "Directive",
    # advanced: base classes & registry escape hatch
    "Service",
    "User",
    "get",
    "call_agent",
]
