"""
Tests for the ambient-context refactor (giga-refactor-ctx):
- contextvar request isolation + the `user` proxy
- field-by-field settings salvage that never deletes

These are deliberately self-contained (no app fixture) and drive asyncio
directly, so they run without the legacy v1 `tests/conftest.py`.
"""

import asyncio

from pydantic import BaseModel

import cat.capabilities as capabilities
from cat.context import Ctx, ctx, use_ctx, user
from cat.auth.user import User
from cat.settings import SettingsManager
from cat.types import Message, TextContent


def _user(name: str) -> User:
    from uuid import uuid5, NAMESPACE_DNS
    return User(id=uuid5(NAMESPACE_DNS, name), name=name)


# ---------------------------------------------------------------------------
# Request context isolation
# ---------------------------------------------------------------------------

def test_concurrent_requests_are_isolated():
    """Two interleaved tasks each observe their own user via the live proxy."""

    alice, bob = _user("alice"), _user("bob")
    seen: dict[str, str] = {}

    async def handler(label: str, u: User):
        with use_ctx(Ctx(user=u)):
            # yield control so the other task interleaves on the loop
            await asyncio.sleep(0)
            # read through the imported live proxy
            seen[label] = user.name
            await asyncio.sleep(0)
            assert user.name == u.name  # still ours after interleaving

    async def main():
        await asyncio.gather(
            handler("A", alice),
            handler("B", bob),
        )

    asyncio.run(main())
    assert seen == {"A": "alice", "B": "bob"}


def test_user_outside_request_raises():
    """Reading the proxy with no active request raises a clear error."""

    async def main():
        try:
            _ = user.id
        except RuntimeError as e:
            assert "request" in str(e).lower()
            return
        raise AssertionError("expected RuntimeError outside a request")

    asyncio.run(main())


def test_ctx_resets_after_block():
    async def main():
        assert ctx_is_empty()
        with use_ctx(Ctx(user=_user("alice"))):
            assert ctx().user.name == "alice"
        assert ctx_is_empty()

    def ctx_is_empty() -> bool:
        try:
            ctx()
            return False
        except RuntimeError:
            return True

    asyncio.run(main())


# ---------------------------------------------------------------------------
# Settings salvage
# ---------------------------------------------------------------------------

class _Settings(BaseModel):
    api_key: str = "default-key"
    timeout: int = 30
    enabled: bool = True


class _FakeService:
    plugin_id = "test"
    service_type = "fakes"
    slug = "fake"

    @classmethod
    async def settings_schema(cls, app):
        return _Settings


def _load_with_raw(monkeypatch_value):
    """Run SettingsManager.load() with DB.load stubbed to return a fixed blob."""
    mgr = SettingsManager()

    async def fake_db_load(key, default=None):
        return monkeypatch_value

    import cat.settings as settings_mod
    original = settings_mod.DB.load
    settings_mod.DB.load = staticmethod(fake_db_load)
    try:
        return asyncio.run(mgr.load(_FakeService, app=None))
    finally:
        settings_mod.DB.load = original


def test_salvage_corrupted_blob_falls_back_to_defaults():
    result = _load_with_raw(["not", "a", "dict"])  # corrupted
    assert result.api_key == "default-key"
    assert result.timeout == 30


def test_salvage_keeps_valid_fields_defaults_poisoned():
    # timeout poisoned (not an int); api_key still valid → keep it, default timeout
    result = _load_with_raw({"api_key": "real-key", "timeout": "not-an-int"})
    assert result.api_key == "real-key"   # salvaged
    assert result.timeout == 30           # reverted to default


def test_salvage_unknown_field_ignored_known_kept():
    # schema changed: stored has an extra field no longer in the model
    result = _load_with_raw({"api_key": "real-key", "removed_field": "x"})
    assert result.api_key == "real-key"
    assert not hasattr(result, "removed_field")


def test_valid_blob_loads_as_is():
    result = _load_with_raw({"api_key": "k", "timeout": 5, "enabled": False})
    assert result.api_key == "k"
    assert result.timeout == 5
    assert result.enabled is False


# ---------------------------------------------------------------------------
# llm() empty-messages promotion (Anthropic rejects an empty messages array)
# ---------------------------------------------------------------------------

class _RecordingProvider:
    """Captures what llm() forwards to the provider."""

    def __init__(self):
        self.seen = {}

    async def llm(self, model, messages, system_prompt="", tools=[], on_token=None, on_tool_call=None):
        self.seen = {"model": model, "messages": messages, "system_prompt": system_prompt}
        return Message(role="assistant", content=[TextContent(text="ok")])


class _FakeApp:
    def __init__(self, provider):
        self._provider = provider

    async def get(self, type, slug, raise_error=True):
        return self._provider


def _call_llm(system_prompt, messages, monkeypatch_provider):
    """Run capabilities.llm() with app() stubbed to return a recording provider."""
    original_app = capabilities.app
    capabilities.app = lambda: _FakeApp(monkeypatch_provider)
    try:
        # model= bypasses the core-settings default lookup
        return asyncio.run(capabilities.llm(
            system_prompt, model="fake:fake", messages=messages, stream=False,
        ))
    finally:
        capabilities.app = original_app


def test_empty_messages_promotes_prompt_to_user_message():
    provider = _RecordingProvider()
    _call_llm("tell me a joke", [], provider)

    msgs = provider.seen["messages"]
    assert len(msgs) == 1
    assert msgs[0].role == "user"          # first message is user, never empty
    assert msgs[0].text == "tell me a joke"
    assert provider.seen["system_prompt"] == ""  # prompt moved into the turn


def test_existing_messages_keep_system_prompt():
    provider = _RecordingProvider()
    existing = [Message(role="user", content=[TextContent(text="hi")])]
    _call_llm("you are helpful", existing, provider)

    # With real messages present, the system prompt stays a system prompt.
    assert provider.seen["system_prompt"] == "you are helpful"
    assert provider.seen["messages"] == existing
