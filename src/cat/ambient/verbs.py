"""
Ambient utilities to avoid deeply nested objects.

The actions you *call*: `llm`, `embedder`, `hook`, `execute_hook`, `agui_event`,
`call_agent`. (The ambient *nouns* you read — `user`, `plugin` — live in
`cat.ambient.context_vars` and `cat.ambient.runtime`.)

`from cat import llm, embedder, hook` binds *names to functions*.
Importing builds nothing; each function resolves the configured implementation
lazily through the registry when it is *called*. That is what lets the nice
import surface coexist with runtime/plugin/config selection: the name is fixed,
the behaviour is late-bound.

Streaming is sourced from the request context (`ctx().stream`), never from a
`self.request` back-reference.
"""

import json
import time
from uuid import uuid4
from typing import TYPE_CHECKING

from cat.ambient.context_vars import ctx
from cat.ambient.runtime import ccat
from cat.protocols.agui import events

if TYPE_CHECKING:
    from cat.types import Message, Task, TaskResult
    from cat.mad_hatter.decorators import Tool
    from cat.auth.user import User


# ---------------------------------------------------------------------------
# Streaming to the current client (resolved from the request context)
# ---------------------------------------------------------------------------

async def send_json(data: dict) -> None:
    """Send raw JSON to the current client, if one is streaming."""
    stream = ctx().stream
    if stream is not None:
        await stream(data)


async def agui_event(event: "events.BaseEvent") -> None:
    """Send an AGUI event to the current client."""
    stream = ctx().stream
    if stream is not None:
        # Keep the typed event intact so the protocol encoder can apply aliases
        # such as messageId, toolCallId and rawEvent at the transport boundary.
        await stream(event)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

def _split_slug(slug: str) -> tuple[str, str]:
    """Parse a "provider:model" slug into (provider_slug, model_slug)."""
    if ":" in slug:
        provider_slug, model_slug = slug.split(":", 1)
    else:
        provider_slug, model_slug = "default", slug
    return provider_slug, model_slug


async def _default_model_slug(field: str) -> str:
    core = await ccat().get("config", "core")
    settings = await core.load_settings()
    return getattr(settings, field)


async def llm(
    system_prompt: str = "",
    model: str | None = None,
    messages: "list[Message] | None" = None,
    tools: "list[Tool] | None" = None,
    stream: bool = True,
) -> "Message":
    """
    Generate a response with the configured Large Language Model.

    Resolves the configured default provider at call time, or an explicit
    `model="provider:model"`. Streams tokens to the current client via the
    request context's stream callback.
    """
    messages = list(messages) if messages else []
    tools = tools or []

    slug = model or await _default_model_slug("default_llm")
    provider_slug, model_slug = _split_slug(slug)
    provider = await ccat().get("model_providers", provider_slug, raise_error=True)

    # The Anthropic Messages API rejects an empty `messages` array (400) and
    # requires the first message to be role="user" — the system prompt is a
    # separate field, not a turn. OpenAI-compatible providers tolerate a
    # system-only call, but to behave the same everywhere, when there are no
    # messages we promote the prompt to the first user message.
    if not messages:
        from cat.types import Message, TextContent
        messages = [Message(role="user", content=[TextContent(text=system_prompt)])]
        system_prompt = ""

    # One id for this whole response: Start, every Content delta and End carry
    # it, so a client can correlate the pieces of one message (and tell two
    # concurrent responses apart). A fresh uuid per event would make that
    # impossible.
    message_id = str(uuid4())

    # Stream text tokens as AGUI events.
    on_token = None
    text_started = False
    if stream:
        async def on_token(token: str):
            nonlocal text_started
            if not token:
                return
            if not text_started:
                await agui_event(events.TextMessageStartEvent(
                    message_id=message_id, timestamp=int(time.time() * 1000)
                ))
                text_started = True
            await agui_event(events.TextMessageContentEvent(
                message_id=message_id,
                delta=token,
                timestamp=int(time.time() * 1000),
            ))

    async def on_tool_call(tool_call):
        await agui_event(events.ToolCallStartEvent(
            timestamp=int(time.time() * 1000),
            tool_call_id=str(tool_call.id),
            tool_call_name=tool_call.name,
            parent_message_id=message_id,
        ))
        await agui_event(events.ToolCallArgsEvent(
            timestamp=int(time.time() * 1000),
            tool_call_id=str(tool_call.id),
            # AG-UI tool argument deltas are JSON fragments, not Python repr.
            delta=json.dumps(tool_call.args),
            raw_event=tool_call.model_dump(),
        ))
        await agui_event(events.ToolCallEndEvent(
            timestamp=int(time.time() * 1000),
            tool_call_id=str(tool_call.id),
        ))

    result = await provider.llm(
        model_slug, messages, system_prompt, tools, on_token, on_tool_call
    )

    if text_started:
        await agui_event(events.TextMessageEndEvent(
            message_id=message_id, timestamp=int(time.time() * 1000)
        ))

    return result


async def embedder(text: str, model: str | None = None) -> list[float]:
    """Embed text with the configured embedder (or an explicit `model=`)."""
    slug = model or await _default_model_slug("default_embedder")
    provider_slug, model_slug = _split_slug(slug)
    provider = await ccat().get("model_providers", provider_slug, raise_error=True)

    vector = await provider.embed(model_slug, text)
    if vector is None:
        raise RuntimeError(
            f"Provider '{provider_slug}' does not support embeddings. "
            "Configure a different default embedder, or implement embed() on the provider."
        )
    return vector


# ---------------------------------------------------------------------------
# Auth — framework plumbing, not a plugin-facing capability.
#
# `auth()` is what the request-context middleware calls once per request to
# populate `ctx().user` (see cat.startup). It is intentionally NOT exported from
# the `cat` front door: plugins read the already-authenticated `user`, they do
# not re-run authentication. Imported as `from cat.ambient import auth`.
# ---------------------------------------------------------------------------

async def auth(request, role: str | None = None) -> "User | None":
    """
    Authenticate a request against the registered auth handlers, returning the
    first `User` produced. Optionally enforce a role.

    Handlers are tried by descending `priority` (ties keep registration order),
    so which one wins is a property a plugin declares rather than an accident of
    discovery order.
    """
    from cat.auth.user import User

    handlers = await ccat().get_all("auths")
    ordered = sorted(handlers.values(), key=lambda h: -h.priority)
    for handler in ordered:
        candidate = await handler.authenticate(request)
        if candidate and isinstance(candidate, User):
            if role and not candidate.has_role(role):
                return None
            return candidate
    return None


# ---------------------------------------------------------------------------
# Hooks — define with @hook, fire with await execute_hook(name, value)
# ---------------------------------------------------------------------------
#
# Hooks vs directives — the one rule
# ----------------------------------
#   Need the agent?  -> write a Directive (agent-scoped, stateful, opt-in).
#   Transform a global pipeline event?  -> write a hook.
# A hook is data-only: it never receives the agent. Reaching the agent is the
# directive's job.
#
# The core hook catalog (five lifecycle events)
# ---------------------------------------------
#   Hook                  | Value       | Fires
#   ----------------------|-------------|------------------------------------
#   before_cat_bootstrap  | None        | app starting, after plugin discovery
#   after_cat_bootstrap   | None        | app ready
#   after_plugins_reload  | None        | plugins/endpoints/services reindexed
#   before_agent_run      | Task        | an agent is about to run (message in)
#   after_agent_run       | TaskResult  | an agent finished (message out)
# Plugins may also define and fire their own hooks by any name (the `uploads`
# plugin's `after_file_upload(UploadedFile)` is the reference example); they
# follow the same single-value, data-only, in-place-mutation contract.
#
# In-place mutation
# -----------------
# A handler receives exactly one argument: the piped value. Mutate it in place
# and return nothing — the change survives to the next handler and the caller,
# because the pipe keeps the same reference on a None return. Return a value
# only to replace the object wholesale. `None`-valued hooks are pure reactions.
#
# Ambient contract (what you can reach from inside a hook)
# --------------------------------------------------------
#   ccat()  -> always available.
#   user    -> request-scoped: resolves in before_agent_run / after_agent_run
#              (and plugin request hooks like after_file_upload); raises
#              RuntimeError in the bootstrap/reload hooks (no active request).
#
# v1 -> v2 migration
# ------------------
#   after_mad_hatter_refresh                 -> after_plugins_reload (rename)
#   before/after_agent_execution             -> before/after_agent_run (rename)
#   before/after_{slug}_agent_execution      -> a Directive on that agent
#   agent_prompt_prefix / _suffix            -> a Directive: append to
#                                               agent.system_prompt in start()/step()
#   agent_{slug}_prompt_prefix / _suffix     -> same, attached to that agent only
#   agent_allowed_tools                      -> a Directive: mutate agent.tools in start()


async def execute_hook(name: str, value=None):
    """
    Fire a hook from anywhere, returning the (possibly mutated) value:

        value = await execute_hook("before_agent_run", value)

    Handlers run priority-first with error isolation. Each receives exactly one
    argument (the piped value) and may mutate it in place (no return needed) or
    return a replacement. See the module section above for the core catalog, the
    ambient contract, and the v1->v2 migration table.
    """
    return await ccat().mad_hatter.execute_hook(name, value)


def hook(*args, priority: int = 1):
    """
    Decorator to *define* a hook:

        `@hook`, `@hook("custom_name")`, `@hook(priority=2)`

    A hook handler takes exactly one argument — the piped value — and is
    data-only: it never receives the agent (that's a directive's job). Mutate
    the value in place, or return a replacement. To *fire* a hook, use
    `await execute_hook(name, value)`.
    """
    from cat.mad_hatter.decorators import hook as hook_decorator
    return hook_decorator(*args, priority=priority)


# ---------------------------------------------------------------------------
# Registry escape hatch + agents
# ---------------------------------------------------------------------------

async def get(type: str, slug: str, raise_error: bool = True):
    """Low-level registry escape hatch. Rarely needed — prefer the capabilities."""
    return await ccat().get(type, slug, raise_error=raise_error)


async def get_all(type: str):
    """Every registered service of a type, keyed by slug.

    The plural of `get`, for the rare case where you need the whole set rather
    than one by name (e.g. trying each auth handler in turn).
    """
    return await ccat().get_all(type)


async def call_agent(slug: str, task: "Task") -> "TaskResult":
    """Run another agent by slug. No request threading required."""
    agent = await ccat().get("agents", slug, raise_error=True)
    return await agent(task)
