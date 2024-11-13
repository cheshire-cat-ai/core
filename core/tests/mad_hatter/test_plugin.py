import os
import pytest
import fnmatch
import subprocess

from inspect import isfunction

from tests.conftest import clean_up_mocks

from cat.mad_hatter.mad_hatter import Plugin
from cat.mad_hatter.decorators import CatHook, CatTool, CustomEndpoint

mock_plugin_path = "tests/mocks/mock_plugin/"


# this fixture will give test functions a ready instantiated plugin
# (and having the `client` fixture, a clean setup every unit)
@pytest.fixture
def plugin(client):
    p = Plugin(mock_plugin_path)
    yield p


def test_create_plugin_wrong_folder():
    with pytest.raises(Exception) as e:
        Plugin("/non/existent/folder")

    assert "Cannot create" in str(e.value)


def test_create_plugin_empty_folder():
    path = "tests/mocks/empty_folder"

    os.mkdir(path)

    with pytest.raises(Exception) as e:
        Plugin(path)

    assert "Cannot create" in str(e.value)


def test_create_plugin(plugin):
    assert not plugin.active

    assert plugin.path == mock_plugin_path
    assert plugin.id == "mock_plugin"

    # manifest
    assert isinstance(plugin.manifest, dict)
    assert plugin.manifest["id"] == plugin.id
    assert plugin.manifest["name"] == "MockPlugin"
    assert "Description not found" in plugin.manifest["description"]

    # hooks and tools
    assert plugin.hooks == []
    assert plugin.tools == []
    assert plugin.endpoints == []


def test_activate_plugin(plugin):
    # activate it
    plugin.activate()

    assert plugin.active is True

    # hooks
    assert len(plugin.hooks) == 3
    for hook in plugin.hooks:
        assert isinstance(hook, CatHook)
        assert hook.plugin_id == "mock_plugin"
        assert hook.name in [
            "factory_allowed_llms",
            "before_cat_sends_message",
        ]
        assert isfunction(hook.function)

        if hook.name == "before_cat_sends_message":
            assert hook.priority > 1
        else:
            assert hook.priority == 1  # default priority

    # tools
    assert len(plugin.tools) == 1
    tool = plugin.tools[0]
    assert isinstance(tool, CatTool)
    assert tool.plugin_id == "mock_plugin"
    assert tool.name == "mock_tool"
    assert tool.description == "Used to test mock tools. Input is the topic."
    assert isfunction(tool.func)
    assert tool.return_direct is True
    # tool examples found
    assert len(tool.start_examples) == 2
    assert "mock tool example 1" in tool.start_examples
    assert "mock tool example 2" in tool.start_examples

    # endpoints
    assert len(plugin.endpoints) == 4
    for endpoint in plugin.endpoints:
        assert isinstance(endpoint, CustomEndpoint)
        assert endpoint.plugin_id == "mock_plugin"


def test_deactivate_plugin(plugin):
    
    # activate plugin
    plugin.activate()

    # deactivate it
    plugin.deactivate()

    # decorators
    assert len(plugin.hooks) == 0
    assert len(plugin.tools) == 0
    assert len(plugin.endpoints) == 0
    

def test_settings_schema(plugin):
    settings_schema = plugin.settings_schema()
    assert isinstance(settings_schema, dict)
    assert settings_schema["properties"] == {}
    assert settings_schema["title"] == "PluginSettingsModel"
    assert settings_schema["type"] == "object"


def test_load_settings(plugin):
    settings = plugin.load_settings()
    assert settings == {}


def test_save_settings(plugin):
    fake_settings = {"a": 42}
    plugin.save_settings(fake_settings)

    settings = plugin.load_settings()
    assert settings["a"] == fake_settings["a"]


# Check if plugin requirements have been installed
# ATTENTION: not using `plugin` fixture here, we instantiate and cleanup manually
#           to use the unmocked Plugin class
def test_install_plugin_dependencies():
    # manual cleanup
    clean_up_mocks()
    # Uninstall mock plugin requirements
    os.system("pip uninstall -y pip-install-test")

    # Install mock plugin
    p = Plugin(mock_plugin_path)

    # Dependencies are installed on plugin activation
    p.activate()

    # pip-install-test should have been installed
    result = subprocess.run(["pip", "list"], stdout=subprocess.PIPE)
    result = result.stdout.decode()
    assert fnmatch.fnmatch(result, "*pip-install-test*")

    # manual cleanup
    clean_up_mocks()
    # Uninstall mock plugin requirements
    os.system("pip uninstall -y pip-install-test")
