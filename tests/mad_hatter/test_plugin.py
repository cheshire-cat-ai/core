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

# the test harness's `isolated_project` autouse fixture stubs this out for every
# test (see cat/testing/__init__.py) to skip real dependency installs; grab the
# real implementation here, at collection time, before any test patches it
_REAL_INSTALL_REQUIREMENTS = Plugin._install_requirements


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


def test_install_requirements_trailing_newline(plugin):
    # readlines() keeps line terminators, so every requirements.txt (they
    # virtually always end with one) hands `Requirement()` a trailing "\n".
    req_file = os.path.join(plugin.path, "requirements.txt")
    with open(req_file, "w") as f:
        f.write("some-never-installed-package==1.2.3\nanother-missing-package\n")

    written = {}

    def capture_written_requirements(args, **kwargs):
        # the temp requirements file is deleted as soon as `_install_requirements`
        # exits its `with`, so read it back from inside the mocked subprocess call
        with open(args[-1]) as f:
            written["content"] = f.read()

    with (
        patch("cat.mad_hatter.plugin.log.error") as mock_log_error,
        patch("cat.mad_hatter.plugin.subprocess.run", side_effect=capture_written_requirements) as mock_run,
    ):
        _REAL_INSTALL_REQUIREMENTS(plugin)

        # a parse failure is swallowed into a generic log.error, so asserting
        # it was never called is what catches the regression
        mock_log_error.assert_not_called()
        mock_run.assert_called_once()

    assert "some-never-installed-package==1.2.3" in written["content"]
    assert "another-missing-package" in written["content"]
