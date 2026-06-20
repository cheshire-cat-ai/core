"""
Ambient verbs (`cat.ambient.verbs`) — the actions plugins *call*.

Pure helpers and late-bound behaviour are exercised here without a full app
where possible; `execute_hook` uses the booted app to prove the no-hook path.
"""

import asyncio

import pytest

from cat.ambient import verbs
from cat.types import Message, TextContent


# --- slug parsing ----------------------------------------------------------

def test_split_slug_with_provider():
    assert verbs._split_slug("openai:gpt-4") == ("openai", "gpt-4")


def test_split_slug_defaults_provider():
    assert verbs._split_slug("gpt-4") == ("default", "gpt-4")


def test_split_slug_keeps_extra_colons_in_model():
    assert verbs._split_slug("prov:a:b") == ("prov", "a:b")


# --- llm() empty-messages promotion ----------------------------------------
# The Anthropic Messages API rejects an empty `messages` array and requires the
# first message to be role="user"; verbs.llm() promotes the system prompt to a
# first user message when there are no messages.

class _RecordingProvider:
    def __init__(self):
        self.seen = {}

    async def llm(self, model, messages, system_prompt="", tools=[], on_token=None, on_tool_call=None):
        self.seen = {"model": model, "messages": messages, "system_prompt": system_prompt}
        return Message(role="assistant", content=[TextContent(text="ok")])


class _FakeCat:
    def __init__(self, provider):
        self._provider = provider

    async def get(self, type, slug, raise_error=True):
        return self._provider


def _call_llm(monkeypatch, system_prompt, messages, provider):
    # model= bypasses the core-settings default lookup; stream=False avoids
    # touching the request context.
    monkeypatch.setattr(verbs, "ccat", lambda: _FakeCat(provider))
    return asyncio.run(
        verbs.llm(system_prompt, model="fake:fake", messages=messages, stream=False)
    )


def test_empty_messages_promotes_prompt_to_user_message(monkeypatch):
    provider = _RecordingProvider()
    _call_llm(monkeypatch, "tell me a joke", [], provider)

    msgs = provider.seen["messages"]
    assert len(msgs) == 1
    assert msgs[0].role == "user"
    assert msgs[0].content[0].text == "tell me a joke"
    assert provider.seen["system_prompt"] == ""  # prompt moved into the turn


def test_existing_messages_keep_system_prompt(monkeypatch):
    provider = _RecordingProvider()
    existing = [Message(role="user", content=[TextContent(text="hi")])]
    _call_llm(monkeypatch, "you are helpful", existing, provider)

    assert provider.seen["system_prompt"] == "you are helpful"
    assert provider.seen["messages"] == existing


# --- execute_hook no-op path -----------------------------------------------

def test_execute_hook_unknown_returns_default(client):
    """Firing a hook no plugin defines returns the piped value unchanged."""
    out = asyncio.run(verbs.execute_hook("a_hook_no_one_defines", "passthrough"))
    assert out == "passthrough"
