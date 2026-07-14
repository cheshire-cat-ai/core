import os
import pytest
import shutil

from inspect import isfunction
from unittest.mock import patch

from tests.utils import get_mock_plugin_info

from cat.mad_hatter.mad_hatter import Plugin
from cat.mad_hatter.decorators import Hook, Endpoint
from cat.mad_hatter.plugin_manifest import PluginManifest
from cat.services.service import Service
from cat import config

# The `cat.testing` autouse fixture monkeypatches Plugin._install_requirements
# to a no-op for every test (to avoid real package installs). Capture the real
# implementation here, at module import time, before any test-scoped monkeypatch
# has run, so test_install_requirements_skips_invalid_lines can exercise it.
_real_install_requirements = Plugin._install_requirements


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
        assert hook.name == "after_agent_run"
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


def test_install_requirements_skips_invalid_lines(client):
    """A blank line or comment in requirements.txt (both completely standard
    syntax) must not abort processing of the rest of the file - every valid
    requirement after it should still be queued for install."""

    plugin_path = os.path.join(config.PLUGINS_PATH, "req_plugin")
    os.makedirs(plugin_path)
    with open(os.path.join(plugin_path, "requirements.txt"), "w") as f:
        f.write("# core deps\nsome-fake-package-aaa\nsome-fake-package-bbb\n")

    plugin = Plugin.__new__(Plugin)
    plugin._path = plugin_path
    plugin._id = "req_plugin"

    captured = {}

    def fake_run(args, **kwargs):
        with open(args[-1]) as tmp:
            captured["content"] = tmp.read()

        class Result:
            returncode = 0

        return Result()

    with patch("importlib.metadata.distributions", return_value=[]), patch(
        "subprocess.run", side_effect=fake_run
    ):
        _real_install_requirements(plugin)

    assert captured["content"] == "some-fake-package-aaa\nsome-fake-package-bbb"

    shutil.rmtree(plugin_path)
