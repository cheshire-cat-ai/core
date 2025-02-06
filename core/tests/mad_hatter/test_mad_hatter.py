import os
import pytest
from inspect import isfunction

import cat.utils as utils

from cat.mad_hatter.mad_hatter import MadHatter, Plugin
from cat.mad_hatter.decorators import CatHook, CatTool

from tests.utils import create_mock_plugin_zip


# this function will be run before each test function
@pytest.fixture(scope="function")
def mad_hatter(client):  # client here injects the monkeypatched version of the cat
    # each test is given the mad_hatter instance (it's a singleton)
    yield MadHatter()


def test_instantiation_discovery(mad_hatter):
    # Mad Hatter finds core_plugin
    assert list(mad_hatter.plugins.keys()) == ["core_plugin"]
    assert isinstance(mad_hatter.plugins["core_plugin"], Plugin)
    assert "core_plugin" in mad_hatter.load_active_plugins_from_db()

    # finds hooks
    assert len(mad_hatter.hooks.keys()) > 0
    for hook_name, hooks_list in mad_hatter.hooks.items():
        assert len(hooks_list) == 1  # core plugin implements each hook
        h = hooks_list[0]
        assert isinstance(h, CatHook)
        assert h.plugin_id == "core_plugin"
        assert isinstance(h.name, str)
        assert isfunction(h.function)
        assert h.priority == 0.0

    # finds tool
    assert len(mad_hatter.tools) == 1
    tool = mad_hatter.tools[0]
    assert isinstance(tool, CatTool)
    assert tool.plugin_id == "core_plugin"
    assert tool.name == "get_the_time"
    assert (
        tool.description
        == "Useful to get the current time when asked. Input is always None."
    )
    assert isfunction(tool.func)
    assert not tool.return_direct
    assert len(tool.start_examples) == 2
    assert "what time is it" in tool.start_examples
    assert "get the time" in tool.start_examples

    # list of active plugins in DB is correct
    active_plugins = mad_hatter.load_active_plugins_from_db()
    assert len(active_plugins) == 1
    assert active_plugins[0] == "core_plugin"


# installation tests will be run for both flat and nested plugin
@pytest.mark.parametrize("plugin_is_flat", [True, False])
def test_plugin_install(mad_hatter: MadHatter, plugin_is_flat):
    # install plugin
    new_plugin_zip_path = create_mock_plugin_zip(flat=plugin_is_flat)
    mad_hatter.install_plugin(new_plugin_zip_path)

    # archive extracted
    assert os.path.exists(os.path.join(utils.get_plugins_path(), "mock_plugin"))

    # plugins list updated
    assert list(mad_hatter.plugins.keys()) == ["core_plugin", "mock_plugin"]
    assert isinstance(mad_hatter.plugins["mock_plugin"], Plugin)
    assert (
        "mock_plugin" in mad_hatter.load_active_plugins_from_db()
    )  # plugin starts active

    # plugin is activated by default
    assert len(mad_hatter.plugins["mock_plugin"].hooks) == 3
    assert len(mad_hatter.plugins["mock_plugin"].tools) == 1
    assert len(mad_hatter.plugins["mock_plugin"].forms) == 1
    assert len(mad_hatter.plugins["mock_plugin"].endpoints) == 6

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

    # found tool and hook have been cached
    mock_hook_name = "before_cat_sends_message"
    assert len(mad_hatter.hooks[mock_hook_name]) == 3  # one in core, two in mock plugin
    expected_priorities = [3, 2, 0]
    for hook_idx, cached_hook in enumerate(mad_hatter.hooks[mock_hook_name]):
        assert cached_hook.name == mock_hook_name
        assert (
            cached_hook.priority == expected_priorities[hook_idx]
        )  # correctly sorted by priority
        if cached_hook.plugin_id != "core_plugin":
            assert cached_hook.plugin_id == "mock_plugin"
            assert id(cached_hook) in hooks_ram_addresses  # same object in memory!

    # list of active plugins in DB is correct
    active_plugins = mad_hatter.load_active_plugins_from_db()
    assert len(active_plugins) == 2
    assert "core_plugin" in active_plugins
    assert "mock_plugin" in active_plugins


def test_plugin_uninstall_non_existent(mad_hatter: MadHatter):
    # should not throw error
    assert len(mad_hatter.plugins) == 1  # core_plugin
    mad_hatter.uninstall_plugin("wrong_plugin")
    assert len(mad_hatter.plugins) == 1

    # list of active plugins in DB is correct
    active_plugins = mad_hatter.load_active_plugins_from_db()
    assert len(active_plugins) == 1
    assert active_plugins[0] == "core_plugin"


@pytest.mark.parametrize("plugin_is_flat", [True, False])
def test_plugin_uninstall(mad_hatter: MadHatter, plugin_is_flat):
    # install plugin
    new_plugin_zip_path = create_mock_plugin_zip(flat=plugin_is_flat)
    mad_hatter.install_plugin(new_plugin_zip_path)

    # uninstall
    mad_hatter.uninstall_plugin("mock_plugin")

    # directory removed
    assert not os.path.exists(os.path.join(utils.get_plugins_path(), "mock_plugin"))

    # plugins list updated
    assert "mock_plugin" not in mad_hatter.plugins.keys()
    # plugin cache updated (only core_plugin stuff)
    assert len(mad_hatter.hooks) > 0
    for h_name, h_list in mad_hatter.hooks.items():
        assert len(h_list) == 1
        assert h_list[0].plugin_id == "core_plugin"
    assert len(mad_hatter.tools) == 1
    assert len(mad_hatter.forms) == 0
    assert len(mad_hatter.endpoints) == 0

    # list of active plugins in DB is correct
    active_plugins = mad_hatter.load_active_plugins_from_db()
    assert len(active_plugins) == 1
    assert active_plugins[0] == "core_plugin"
