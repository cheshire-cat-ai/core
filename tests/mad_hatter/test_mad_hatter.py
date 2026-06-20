import os
import pytest
import pytest_asyncio

from cat import config
from cat.ambient.runtime import ccat
from cat.mad_hatter.mad_hatter import MadHatter, Plugin

from tests.utils import create_mock_plugin_zip, get_mock_plugin_info


# async_client bootstraps the cat in the test's own event loop (no blocking
# TestClient portal inside an async test), so ccat() is live here. The core
# suite is core-only, so the cat boots with zero plugins.
@pytest_asyncio.fixture(scope="function")
async def mad_hatter(async_client):
    yield ccat().mad_hatter


# installation tests will be run for both flat and nested plugin
@pytest.mark.parametrize("plugin_is_flat", [True, False])
async def test_plugin_install(mad_hatter: MadHatter, plugin_is_flat):
    # core-only baseline: no plugins before install
    assert set(mad_hatter.plugins.keys()) == set()

    # install plugin
    new_plugin_zip_path = create_mock_plugin_zip(flat=plugin_is_flat)
    await mad_hatter.install_plugin(new_plugin_zip_path)

    # archive extracted
    assert os.path.exists(os.path.join(config.PLUGINS_PATH, "mock_plugin"))

    # plugins list updated
    assert set(mad_hatter.plugins.keys()) == {"mock_plugin"}
    assert isinstance(mad_hatter.plugins["mock_plugin"], Plugin)
    # plugin starts active
    assert "mock_plugin" in await mad_hatter.get_active_plugins()

    # plugin contains cat decorators (v2 Plugin: hooks / endpoints / services)
    plugin = mad_hatter.plugins["mock_plugin"]
    assert len(plugin.hooks) == get_mock_plugin_info()["hooks"]
    assert len(plugin.endpoints) == get_mock_plugin_info()["endpoints"]
    assert len(plugin.services) == get_mock_plugin_info()["services"]

    # hooks carry the owning plugin id
    for h in plugin.hooks:
        assert h.plugin_id == "mock_plugin"

    # hooks are cached in mad_hatter, sorted by priority (mock sets 3 then 2)
    cached_hooks = mad_hatter.hooks["before_cat_sends_message"]
    assert [h.priority for h in cached_hooks] == [3, 2]
    for cached_hook in cached_hooks:
        assert cached_hook.name == "before_cat_sends_message"
        assert cached_hook.plugin_id == "mock_plugin"
        assert id(cached_hook) in {id(h) for h in plugin.hooks}  # same objects

    # list of active plugins in DB is correct
    assert "mock_plugin" in await mad_hatter.get_active_plugins()


async def test_plugin_uninstall_non_existent(mad_hatter: MadHatter):
    # core-only baseline
    assert set(mad_hatter.plugins.keys()) == set()

    with pytest.raises(Exception):
        await mad_hatter.uninstall_plugin("wrong_plugin")

    # still the same plugins
    assert set(mad_hatter.plugins.keys()) == set()
    assert set(await mad_hatter.get_active_plugins()) == set()


@pytest.mark.parametrize("plugin_is_flat", [True, False])
async def test_plugin_uninstall(mad_hatter: MadHatter, plugin_is_flat):
    # install plugin
    new_plugin_zip_path = create_mock_plugin_zip(flat=plugin_is_flat)
    await mad_hatter.install_plugin(new_plugin_zip_path)

    # uninstall
    await mad_hatter.uninstall_plugin("mock_plugin")

    # directory removed
    assert not os.path.exists(os.path.join(config.PLUGINS_PATH, "mock_plugin"))

    # plugins list updated
    assert "mock_plugin" not in mad_hatter.plugins.keys()

    # list of active plugins in DB is correct
    assert set(await mad_hatter.get_active_plugins()) == set()
