import pytest
import pytest_asyncio

from cat.ambient.runtime import ccat
from cat.mad_hatter.mad_hatter import MadHatter
from cat.services.model_providers.openai_compatible import (
    OpenAICompatibleProvider,
    NO_KEY_MESSAGE,
)


# async_client bootstraps the cat in the test's own event loop (no blocking
# TestClient portal inside an async test), so ccat() is the live instance.
# The core suite is core-only: the cat boots with zero plugins.
@pytest_asyncio.fixture(scope="function")
async def cheshire_cat(async_client):
    yield ccat()


async def test_main_modules_loaded(cheshire_cat):
    assert isinstance(cheshire_cat.mad_hatter, MadHatter)


async def test_default_provider_loaded(cheshire_cat):
    # OpenAICompatibleProvider is a core-provided default provider.
    provider = await cheshire_cat.get("model_providers", "openai_compatible")
    assert isinstance(provider, OpenAICompatibleProvider)
    # No key configured in tests: no live models, and llm() replies with a
    # clear next step instead of raising.
    assert await provider.list_llms() == []
    reply = await provider.llm("gpt-4o-mini", messages=[])
    assert reply.text == NO_KEY_MESSAGE


async def test_get_returns_none_when_not_found(cheshire_cat):
    result = await cheshire_cat.get("model_providers", "nonexistent", raise_error=False)
    assert result is None


async def test_get_raises_when_not_found(cheshire_cat):
    with pytest.raises(Exception, match="not found"):
        await cheshire_cat.get("model_providers", "nonexistent")


async def test_get_all_auths_core_only(cheshire_cat):
    # Core-only: no auth plugin is active, so the core "default" fallback handler
    # is present (plugins like simple_oauth would replace it — tested in their
    # own suites).
    auths = await cheshire_cat.get_all("auths")
    assert isinstance(auths, dict)
    assert "default" in auths


async def test_get_all_empty_type(cheshire_cat):
    result = await cheshire_cat.get_all("nonexistent_type")
    assert result == {}
