"""
Ambient capabilities — the `cat` front door.

`from cat import llm, embedder, hook` binds *names to functions*.
Importing builds nothing; each function resolves the configured implementation
lazily through the registry when it is *called*. That is what lets the nice
import surface coexist with runtime/plugin/config selection: the name is fixed,
the behaviour is late-bound.

Streaming is sourced from the request context (`ctx().stream`), never from a
`self.request` back-reference.
"""

import time
from uuid import uuid4
from typing import TYPE_CHECKING

from cat.context import ctx, app
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
    await send_json(dict(event))


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
    core_settings = await app().get("config", "core")
    return getattr(core_settings.settings, field)


async def llm(
    system_prompt: str = "",
    model: str | None = None,
    messages: "list[Message]" = [],
    tools: "list[Tool]" = [],
    stream: bool = True,
) -> "Message":
    """
    Generate a response with the configured Large Language Model.

    Resolves the configured default provider at call time, or an explicit
    `model="provider:model"`. Streams tokens to the current client via the
    request context's stream callback.
    """
    slug = model or await _default_model_slug("default_llm")
    provider_slug, model_slug = _split_slug(slug)
    provider = await app().get("model_providers", provider_slug, raise_error=True)

    # The Anthropic Messages API rejects an empty `messages` array (400) and
    # requires the first message to be role="user" — the system prompt is a
    # separate field, not a turn. OpenAI-compatible providers tolerate a
    # system-only call, but to behave the same everywhere, when there are no
    # messages we promote the prompt to the first user message.
    if not messages:
        from cat.types import Message, TextContent
        messages = [Message(role="user", content=[TextContent(text=system_prompt)])]
        system_prompt = ""

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
                    message_id=str(uuid4()), timestamp=int(time.time())
                ))
                text_started = True
            await agui_event(events.TextMessageContentEvent(
                message_id=str(uuid4()), delta=token, timestamp=int(time.time())
            ))

    async def on_tool_call(tool_call):
        await agui_event(events.ToolCallStartEvent(
            timestamp=int(time.time()),
            tool_call_id=str(tool_call.id),
            tool_call_name=tool_call.name,
        ))
        await agui_event(events.ToolCallArgsEvent(
            timestamp=int(time.time()),
            tool_call_id=str(tool_call.id),
            delta=str(tool_call.args),
            raw_event=tool_call.model_dump(),
        ))
        await agui_event(events.ToolCallEndEvent(
            timestamp=int(time.time()),
            tool_call_id=str(tool_call.id),
        ))

    result = await provider.llm(
        model_slug, messages, system_prompt, tools, on_token, on_tool_call
    )

    if text_started:
        await agui_event(events.TextMessageEndEvent(
            message_id=str(uuid4()), timestamp=int(time.time())
        ))

    return result


async def embedder(text: str, model: str | None = None) -> list[float]:
    """Embed text with the configured embedder (or an explicit `model=`)."""
    slug = model or await _default_model_slug("default_embedder")
    provider_slug, model_slug = _split_slug(slug)
    provider = await app().get("model_providers", provider_slug, raise_error=True)
    return await provider.embed(model_slug, text)


# ---------------------------------------------------------------------------
# Auth — framework plumbing, not a plugin-facing capability.
#
# `auth()` is what the request-context middleware calls once per request to
# populate `ctx().user` (see cat.startup). It is intentionally NOT exported from
# the `cat` front door: plugins read the already-authenticated `user`, they do
# not re-run authentication. Imported as `from cat.capabilities import auth`.
# ---------------------------------------------------------------------------

async def auth(request, role: str | None = None) -> "User | None":
    """
    Authenticate a request against the registered auth handlers, returning the
    first `User` produced. Optionally enforce a role.
    """
    from cat.auth.user import User

    handlers = await app().get_all("auths")
    for handler in handlers.values():
        candidate = await handler.authenticate(request)
        if candidate and isinstance(candidate, User):
            if role and not candidate.has_role(role):
                return None
            return candidate
    return None


# ---------------------------------------------------------------------------
# Hooks — define with @hook, fire with await hook(name, value)
# ---------------------------------------------------------------------------

async def _execute_hook(name: str, value=None):
    return await app().mad_hatter.execute_hook(name, value)


def hook(*args, priority: int = 1):
    """
    Dual purpose:

    - As a decorator to *define* a hook:
        `@hook`, `@hook("custom_name")`, `@hook(priority=2)`
    - As an awaitable to *fire* a hook from anywhere:
        `await hook("after_file_upload", value)`

    The two are told apart by arity: firing passes a name *and* a value.
    """
    # Fire: hook("name", value)
    if len(args) == 2 and isinstance(args[0], str):
        name, value = args
        return _execute_hook(name, value)

    # Define: delegate to the decorator.
    from cat.mad_hatter.decorators import hook as hook_decorator
    return hook_decorator(*args, priority=priority)


# ---------------------------------------------------------------------------
# Registry escape hatch + agents
# ---------------------------------------------------------------------------

async def get(type: str, slug: str, raise_error: bool = True):
    """Low-level registry escape hatch. Rarely needed — prefer the capabilities."""
    return await app().get(type, slug, raise_error=raise_error)


async def call_agent(slug: str, task: "Task") -> "TaskResult":
    """Run another agent by slug. No request threading required."""
    agent = await app().get("agents", slug, raise_error=True)
    return await agent(task)
