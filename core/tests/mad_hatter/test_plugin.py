import os
import pytest
import fnmatch
import subprocess

from inspect import isfunction

from cat.mad_hatter.mad_hatter import Plugin
from cat.mad_hatter.decorators import CatHook, CatTool

mock_plugin_path = "tests/mocks/mock_plugin/"

# this fixture will give test functions a ready instantiated plugin
@pytest.fixture
def plugin():

    p = Plugin(mock_plugin_path)
    
    yield p
    
    settings_file = mock_plugin_path + "settings.json"
    if os.path.exists(settings_file):
        os.remove(settings_file)


def test_create_plugin_wrong_folder():

    with pytest.raises(Exception) as e:
        Plugin("/non/existent/folder")
        
    assert f"Cannot create" in str(e.value)

def test_create_plugin_empty_folder():

    path = "tests/mocks/empty_folder"

    os.mkdir(path)

    with pytest.raises(Exception) as e:
        Plugin(path)
        
    assert f"Cannot create" in str(e.value)


def test_create_plugin(plugin):

    assert plugin.active == False
    
    assert plugin.path == mock_plugin_path
    assert plugin.id == "mock_plugin"

    # manifest
    assert type(plugin.manifest) == dict
    assert plugin.manifest["id"] == plugin.id
    assert plugin.manifest["name"] == "MockPlugin"
    assert "Description not found" in plugin.manifest["description"]

    # Check if plugin requirement is installed
    result = subprocess.run(['pip', 'list'], stdout=subprocess.PIPE)
    result = result.stdout.decode()
    assert fnmatch.fnmatch(result, "*pip-install-test*")

    # hooks and tools
    assert plugin.hooks == []
    assert plugin.tools == []


def test_activate_plugin(plugin):

    # activate it
    plugin.activate()

    assert plugin.active == True

    # hooks
    assert len(plugin.hooks) == 1
    hook = plugin.hooks[0]
    assert isinstance(hook, CatHook)
    assert hook.plugin_id == "mock_plugin"
    assert hook.name == "before_cat_sends_message"
    assert isfunction(hook.function)
    assert hook.priority == 2.0

    # tools
    assert len(plugin.tools) == 1
    tool = plugin.tools[0]
    assert isinstance(tool, CatTool)
    assert tool.plugin_id == "mock_plugin"
    assert tool.name == "mock_tool"
    assert "mock_tool" in tool.description
    assert isfunction(tool.func)
    assert tool.return_direct == True

def test_deactivate_plugin(plugin):

    # The plugin is non active by default
    plugin.activate()

    # deactivate it
    plugin.deactivate()

    assert plugin.active == False
    
    # hooks and tools
    assert len(plugin.hooks) == 0
    assert len(plugin.tools) == 0


def test_settings_schema(plugin):

    settings_schema = plugin.settings_schema()
    assert type(settings_schema) == dict
    assert settings_schema["properties"] == {}
    assert settings_schema["title"] == "PluginSettingsModel"
    assert settings_schema['type'] == 'object'


def test_load_settings(plugin):

    settings = plugin.load_settings()
    assert settings == {}


def test_save_settings(plugin):

    fake_settings = {
        "a": 42
    }    
    plugin.save_settings(fake_settings)
    
    settings = plugin.load_settings()
    assert settings["a"] == fake_settings["a"]

