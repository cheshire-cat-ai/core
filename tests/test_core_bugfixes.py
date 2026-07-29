"""Regressions for the bugs found in the devx audit.

Each test pins one behaviour that used to be wrong: see
`openspec/changes/fix-devx-bugs-and-inconsistencies`.
"""

import pytest

from cat import tool
from cat.base import Agent


async def test_text_events_share_one_message_id(fake_llm, run_agent, booted_app):
    """AGUI Start/Content/End of one response must carry the same message_id.

    They used to get a fresh uuid4 each, so a client could not tell which deltas
    belonged to which message.
    """
    from cat.ambient import llm
    from cat.ambient.context_vars import Ctx, use_ctx

    events = []

    async def collect(data):
        events.append(data)

    fake_llm.reply_text("one two three")

    with use_ctx(Ctx(user=None, stream=collect)):
        await llm("say something", stream=True)

    text_events = [
        event for event in events if event.type.value.startswith("TEXT_MESSAGE")
    ]
    ids = {event.message_id for event in text_events}

    assert len(text_events) >= 3  # start + deltas + end
    assert len(ids) == 1, f"expected one message_id, got {ids}"


async def test_two_responses_get_different_message_ids(fake_llm, booted_app):
    """One id per response — not one id for all time."""
    from cat.ambient import llm
    from cat.ambient.context_vars import Ctx, use_ctx

    events = []

    async def collect(data):
        events.append(data)

    fake_llm.reply_text("first")
    fake_llm.reply_text("second")

    with use_ctx(Ctx(user=None, stream=collect)):
        await llm("a", stream=True)
        await llm("b", stream=True)

    ids = {
        event.message_id
        for event in events
        if event.type.value.startswith("TEXT_MESSAGE")
    }
    assert len(ids) == 2


async def test_tool_call_events_use_json_and_parent_message_id(fake_llm, booted_app):
    """AG-UI tool arguments must be JSON and belong to one assistant message."""
    import json

    from cat.ambient import llm
    from cat.ambient.context_vars import Ctx, use_ctx

    events = []

    async def collect(data):
        events.append(data)

    fake_llm.reply_with_tool("lookup", query="cat")

    with use_ctx(Ctx(user=None, stream=collect)):
        await llm("find the cat", stream=True)

    start = next(event for event in events if event.type.value == "TOOL_CALL_START")
    args = next(event for event in events if event.type.value == "TOOL_CALL_ARGS")

    assert start.parent_message_id is not None
    assert json.loads(args.delta) == {"query": "cat"}


async def test_unsupported_embed_returns_none_not_a_fake_vector():
    """The base must not hand back `[0.0]` — a fake vector poisons search."""
    from cat.services.model_providers.base import ModelProvider

    class Embedless(ModelProvider):
        slug = "embedless"

        async def llm(self, *a, **k):
            pass

    assert await Embedless().embed("m", "text") is None


async def test_embedder_raises_when_provider_cannot_embed(booted_app):
    """`embedder()` turns the None into a clear error, naming the provider."""
    from cat.ambient import embedder
    from cat.ambient.runtime import ccat
    from cat.services.model_providers.base import ModelProvider

    class Embedless(ModelProvider):
        slug = "embedless"

        async def llm(self, *a, **k):
            pass

    ccat().registry.register(Embedless)

    with pytest.raises(RuntimeError, match="does not support embeddings"):
        await embedder("some text", model="embedless:whatever")


async def test_run_survives_a_hallucinated_tool_name(fake_llm, run_agent, booted_app):
    """An unknown tool name is a turn in the loop, not a crash."""
    from cat.ambient.runtime import ccat

    class OneToolAgent(Agent):
        slug = "onetool"

        @tool
        def real_tool(self):
            """A tool that exists."""
            return "real result"

    ccat().registry.register(OneToolAgent)

    fake_llm.reply_with_tool("imaginary_tool")
    fake_llm.reply_text("sorry, retried")

    result = await run_agent("onetool", "do the thing")

    tool_messages = [m for m in result.messages if m.role == "tool"]
    assert len(tool_messages) == 1
    assert "not found" in tool_messages[0].text
    assert "real_tool" in tool_messages[0].text  # the model is told what exists
    assert result.messages[-1].text == "sorry, retried"


async def test_user_exists_mirrors_the_other_stores(booted_app):
    """`User` gained `exists()`, which `Store`/`UserStore` already had."""
    from uuid import uuid4
    from cat.auth.user import User

    user = User(id=uuid4(), name="tester")

    assert await user.exists("todos") is False
    await user.save("todos", ["buy milk"])
    assert await user.exists("todos") is True

    # distinguishes "stored as None" from "never stored" — load() cannot
    await user.save("empty", None)
    assert await user.exists("empty") is True


async def test_llm_default_arguments_are_not_shared(fake_llm, booted_app):
    """`messages=[]` as a default used to be one list shared by every call."""
    from cat.ambient import llm
    from cat.ambient.context_vars import Ctx, use_ctx

    fake_llm.reply_text("one")
    fake_llm.reply_text("two")

    with use_ctx(Ctx(user=None)):
        await llm("first prompt", stream=False)
        await llm("second prompt", stream=False)

    # each call saw exactly its own single promoted user message
    assert len(fake_llm.calls[0].messages) == 1
    assert len(fake_llm.calls[1].messages) == 1


def test_endpoint_name_collision_is_refused():
    """Two endpoints named alike in one module silently lost a route."""
    from cat.mad_hatter.decorators.endpoint import endpoint, forget_module

    forget_module(__name__)

    @endpoint.get("/first")
    def handler():
        pass

    with pytest.raises(ValueError, match="both named 'handler'"):
        @endpoint.get("/second")
        def handler():  # noqa: F811 — the collision is the point
            pass

    forget_module(__name__)


def test_reimporting_the_same_endpoint_is_not_a_collision():
    """A plugin reload re-runs the decorator; that must stay legal."""
    from cat.mad_hatter.decorators.endpoint import endpoint, forget_module

    forget_module(__name__)

    @endpoint.get("/same")
    def stable_handler():
        pass

    @endpoint.get("/same")
    def stable_handler():  # noqa: F811 — identical re-declaration
        pass

    forget_module(__name__)


async def test_auth_handlers_are_tried_by_priority(booted_app):
    """Highest priority wins, regardless of registration order."""
    from cat.ambient.verbs import auth
    from cat.ambient.runtime import ccat
    from cat.auth.user import User
    from cat.base import Auth
    from uuid import uuid5, NAMESPACE_DNS

    class LowPriorityAuth(Auth):
        slug = "low_priority"
        priority = -10

        async def authenticate(self, request):
            return User(id=uuid5(NAMESPACE_DNS, "low"), name="low", roles=["admin"])

    class HighPriorityAuth(Auth):
        slug = "high_priority"
        priority = 10

        async def authenticate(self, request):
            return User(id=uuid5(NAMESPACE_DNS, "high"), name="high", roles=["admin"])

    # registered low-first: without priority, "low" would win
    ccat().registry.register(LowPriorityAuth)
    ccat().registry.register(HighPriorityAuth)

    user = await auth(request=None)
    assert user.name == "high"
