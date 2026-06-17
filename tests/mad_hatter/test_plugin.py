import os
import pytest
import subprocess
import shutil

from inspect import isfunction

from tests.utils import get_mock_plugin_info

from cat.mad_hatter.mad_hatter import Plugin
from cat.mad_hatter.decorators import Hook, Tool, Endpoint
from cat import paths


# this fixture will give test functions a ready instantiated plugin
# (and having the `client` fixture, a clean setup every unit)
@pytest.fixture(scope="function")
def plugin(client):

    mock_plugin_path = paths.PLUGINS_PATH + "/mock_plugin"

    shutil.copytree(
        "tests/mocks/mock_plugin",
        mock_plugin_path
    )

    p = Plugin(mock_plugin_path)
    yield p


def test_create_plugin_wrong_folder():
    with pytest.raises(Exception) as e:
        Plugin("/non/existent/folder")

    assert "Cannot create" in str(e.value)


def test_not_create_plugin_with_empty_folder():
    path = paths.PLUGINS_PATH + "/empty_folder"

    os.mkdir(path)

    with pytest.raises(Exception) as e:
        Plugin(path)

    assert "Cannot create" in str(e.value)
    shutil.rmtree(path)


def test_create_plugin(plugin):

    assert plugin.path == paths.PLUGINS_PATH + "/mock_plugin"
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

    # hooks
    assert len(plugin.hooks) == get_mock_plugin_info()["hooks"]
    for hook in plugin.hooks:
        assert isinstance(hook, Hook)
        assert hook.plugin_id == "mock_plugin"
        assert hook.name in [
            "factory_allowed_llms",
            "before_cat_sends_message",
            "factory_alowed_llms",
            "factory_allowed_embedders"
        ]
        assert isfunction(hook.function)

        if hook.name == "before_cat_sends_message":
            assert hook.priority > 1
        else:
            assert hook.priority == 1  # default priority

    # tools
    assert len(plugin.tools) == get_mock_plugin_info()["tools"]
    tool = plugin.tools[0]
    assert isinstance(tool, Tool)
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
    assert len(plugin.endpoints) == get_mock_plugin_info()["endpoints"]
    for endpoint in plugin.endpoints:
        assert isinstance(endpoint, Endpoint)
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


# utility ot obtain installed python packages
def list_packages():
    result = subprocess.run(["uv", "pip", "list"], stdout=subprocess.PIPE)
    return str(result.stdout.decode())


def test_plugin_dependencies_not_installed_if_plugin_not_present(client):

    # pip-install-test should NOT be installed by default (note we are using the client fixture, not plugin)
    result = list_packages()
    assert "pip-install-test" not in result


# Check if plugin requirements have been installed
def test_install_plugin_dependencies(plugin):

    result = list_packages()
    assert "pip-install-test" in result


# Check if plugin requirements have been uninstalled
def test_uninstall_plugin_dependencies(plugin):

    plugin.deactivate()

    # pip-install-test should have been uninstalled
    result = list_packages()
    assert "pip-install-test" not in result
