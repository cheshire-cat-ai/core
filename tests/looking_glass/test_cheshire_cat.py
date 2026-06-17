import pytest

from cat.mad_hatter.mad_hatter import MadHatter
from cat.services.model_providers.default import DefaultModelProvider


@pytest.fixture(scope="function")
def cheshire_cat(client):
    yield client.app.state.ccat


def test_main_modules_loaded(cheshire_cat):
    assert isinstance(
        cheshire_cat.mad_hatter, MadHatter
    )


@pytest.mark.asyncio
async def test_default_provider_loaded(cheshire_cat):
    provider = await cheshire_cat.get("model_providers", "default")
    assert isinstance(provider, DefaultModelProvider)
    assert await provider.list_llms() == ["default"]


@pytest.mark.asyncio
async def test_get_returns_none_when_not_found(cheshire_cat):
    result = await cheshire_cat.get("model_providers", "nonexistent", raise_error=False)
    assert result is None


@pytest.mark.asyncio
async def test_get_raises_when_not_found(cheshire_cat):
    with pytest.raises(Exception, match="not found"):
        await cheshire_cat.get("model_providers", "nonexistent")


@pytest.mark.asyncio
async def test_get_all_auths(cheshire_cat):
    auths = await cheshire_cat.get_all("auths")
    assert isinstance(auths, dict)
    assert "default" in auths


@pytest.mark.asyncio
async def test_get_all_empty_type(cheshire_cat):
    result = await cheshire_cat.get_all("nonexistent_type")
    assert result == {}
