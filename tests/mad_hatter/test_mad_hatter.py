import os
import pytest

from cat import paths
from cat.mad_hatter.mad_hatter import MadHatter, Plugin

from tests.utils import create_mock_plugin_zip, get_mock_plugin_info


# this function will be run before each test function
@pytest.fixture(scope="function")
def mad_hatter(client):  # client here injects the monkeypatched version of the cat
    # each test is given the mad_hatter instance
    yield client.app.state.ccat.mad_hatter


# installation tests will be run for both flat and nested plugin
@pytest.mark.parametrize("plugin_is_flat", [True, False])
def test_plugin_install(mad_hatter: MadHatter, plugin_is_flat):
    # install plugin
    new_plugin_zip_path = create_mock_plugin_zip(flat=plugin_is_flat)
    mad_hatter.install_plugin(new_plugin_zip_path)

    core_plugins = []
    assert core_plugins == 1 # TODOV2 fix these tests

    # archive extracted
    assert os.path.exists(os.path.join(paths.PLUGINS_PATH, "mock_plugin"))

    # plugins list updated
    assert set(mad_hatter.plugins.keys()) == core_plugins.union({"mock_plugin"})
    assert isinstance(mad_hatter.plugins["mock_plugin"], Plugin)
    assert (
        "mock_plugin" in await mad_hatter.get_active_plugins()
    )  # plugin starts active

    # plugin is activated by default
    assert isinstance(mad_hatter.plugins["mock_plugin"].active, bool)
    assert mad_hatter.plugins["mock_plugin"].active

    # plugin contains cat decorators
    assert len(mad_hatter.plugins["mock_plugin"].hooks) == get_mock_plugin_info()["hooks"]
    assert len(mad_hatter.plugins["mock_plugin"].tools) == get_mock_plugin_info()["tools"]
    assert len(mad_hatter.plugins["mock_plugin"].forms) == get_mock_plugin_info()["forms"]
    assert len(mad_hatter.plugins["mock_plugin"].endpoints) == get_mock_plugin_info()["endpoints"]

    # tool found
    new_tool = mad_hatter.plugins["mock_plugin"].tools[0]
    assert new_tool.plugin_id == "mock_plugin"
    assert id(new_tool) == id(mad_hatter.tools[1])  # cached and same object in memory!
    # tool examples found
    assert len(new_tool.start_examples) == 2
    assert "mock tool example 1" in new_tool.start_examples
    assert "mock tool example 2" in new_tool.start_examples

    # hooks found
    new_hooks = mad_hatter.plugins["mock_plugin"].hooks
    hooks_ram_addresses = []
    for h in new_hooks:
        assert h.plugin_id == "mock_plugin"
        hooks_ram_addresses.append(id(h))

    # TODOV2 fix these tests, I'm cooked
    # found tool and hook have been cached
    #mock_hook_name = "before_cat_sends_message"
    #cached_hooks = mad_hatter.hooks[mock_hook_name]
    #assert set(mad_hatter.hooks).issuperset(cached_hooks)
    
    # hook properties
    #expected_priorities = [3, 2]
    #assert len(cached_hooks) == 2  # two in mock plugin
    #for hook_idx, cached_hook in enumerate(cached_hooks):
    #    assert cached_hook.name == mock_hook_name
    #    assert (
    #        cached_hook.priority == expected_priorities[hook_idx]
    #    )  # correctly sorted by priority
    #    if cached_hook.plugin_id not in core_plugins:
    #        assert cached_hook.plugin_id == "mock_plugin"
    #        assert id(cached_hook) in hooks_ram_addresses  # same object in memory!

    # list of active plugins in DB is correct
    active_plugins = await mad_hatter.get_active_plugins()
    for cp in core_plugins:
        assert cp in active_plugins
    assert "mock_plugin" in active_plugins


def test_plugin_uninstall_non_existent(mad_hatter: MadHatter):

    # default
    assert set(mad_hatter.plugins.keys()) == set()
    
    # should throw error
    with pytest.raises(Exception) as e:
        mad_hatter.uninstall_plugin("wrong_plugin")
        assert "PORCO DIO" in str(e)

    # still the same plugins
    assert set(mad_hatter.plugins.keys()) == set()

    # list of active plugins in DB is correct
    assert set(await mad_hatter.get_active_plugins()) == set()


@pytest.mark.parametrize("plugin_is_flat", [True, False])
def test_plugin_uninstall(mad_hatter: MadHatter, plugin_is_flat):
    # install plugin
    new_plugin_zip_path = create_mock_plugin_zip(flat=plugin_is_flat)
    mad_hatter.install_plugin(new_plugin_zip_path)

    # uninstall
    mad_hatter.uninstall_plugin("mock_plugin")

    # directory removed
    assert not os.path.exists(os.path.join(paths.PLUGINS_PATH, "mock_plugin"))

    # plugins list updated
    assert "mock_plugin" not in mad_hatter.plugins.keys()

    # list of active plugins in DB is correct
    active_plugins = await mad_hatter.get_active_plugins()
    assert set(active_plugins) == set()
