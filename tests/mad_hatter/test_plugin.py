import os
import pytest
import shutil

from inspect import isfunction

from tests.utils import get_mock_plugin_info

from cat.mad_hatter.mad_hatter import Plugin
from cat.mad_hatter.decorators import Hook, Endpoint
from cat.mad_hatter.plugin_manifest import PluginManifest
from cat.services.service import Service
from cat import config


# this fixture gives test functions a ready-instantiated plugin in an isolated
# project (the `client` fixture boots the cat into the per-test tmp folder)
@pytest.fixture(scope="function")
def plugin(client):
    mock_plugin_path = os.path.join(config.PLUGINS_PATH, "mock_plugin")
    shutil.copytree("tests/mocks/mock_plugin", mock_plugin_path)

    yield Plugin(mock_plugin_path)


def test_create_plugin_wrong_folder():
    with pytest.raises(Exception) as e:
        Plugin("/non/existent/folder")

    assert "Cannot create" in str(e.value)


def test_not_create_plugin_with_empty_folder(client):
    path = os.path.join(config.PLUGINS_PATH, "empty_folder")
    os.makedirs(path)

    with pytest.raises(Exception) as e:
        Plugin(path)

    assert "Cannot create" in str(e.value)
    shutil.rmtree(path)


def test_create_plugin(plugin):
    assert plugin.path == os.path.join(config.PLUGINS_PATH, "mock_plugin")
    assert plugin.id == "mock_plugin"

    # manifest is a PluginManifest model (no plugin.json in the mock, so name
    # falls back to the plugin id and the description is the default).
    assert isinstance(plugin.manifest, PluginManifest)
    assert plugin.manifest.name == "mock_plugin"
    assert "Description not found" in plugin.manifest.description

    # decorated objects are only populated after activation
    assert plugin.hooks == []
    assert plugin.endpoints == []
    assert plugin.services == []


def test_activate_plugin(plugin):
    plugin.activate()

    # hooks
    assert len(plugin.hooks) == get_mock_plugin_info()["hooks"]
    for hook in plugin.hooks:
        assert isinstance(hook, Hook)
        assert hook.plugin_id == "mock_plugin"
        assert hook.name == "before_cat_sends_message"
        assert isfunction(hook.function)
        assert hook.priority > 1  # mock hooks set priority 2 and 3

    # endpoints
    assert len(plugin.endpoints) == get_mock_plugin_info()["endpoints"]
    for endpoint in plugin.endpoints:
        assert isinstance(endpoint, Endpoint)
        assert endpoint.plugin_id == "mock_plugin"

    # services (the mock model provider)
    assert len(plugin.services) == get_mock_plugin_info()["services"]
    for service in plugin.services:
        assert issubclass(service, Service)
        assert service.plugin_id == "mock_plugin"


def test_deactivate_plugin(plugin):
    plugin.activate()
    plugin.deactivate()

    assert len(plugin.hooks) == 0
    assert len(plugin.endpoints) == 0
    assert len(plugin.services) == 0
