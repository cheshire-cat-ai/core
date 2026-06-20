"""Registry routes (core capability): browse `/registry` and install via
`POST /registry/install`.

Registry access is network-bound, so both the search (list) and the download are
mocked — these tests exercise core's install plumbing, not the live registry.
"""

import os

from cat import config
from cat.mad_hatter.plugin_manifest import PluginManifest
from tests.utils import create_mock_plugin_zip


async def _fake_download(url: str):
    # stand in for registry_download_plugin: produce a local zip on the fly
    return create_mock_plugin_zip(True)


async def _fake_search_empty(search=None):
    return []


async def _fake_search_nonempty(search=None):
    return [PluginManifest(name="Some Registry Plugin", plugin_url="https://example.com/p")]


def test_list_registry_plugins_empty(client, monkeypatch):
    """With an empty registry, GET /registry returns an empty list (core-only)."""
    monkeypatch.setattr(
        "cat.routes.plugins.plugins_registry.registry_search_plugins", _fake_search_empty
    )

    response = client.get("/registry")
    assert response.status_code == 200
    assert response.json() == []


def test_list_registry_plugins_nonempty(client, monkeypatch):
    monkeypatch.setattr(
        "cat.routes.plugins.plugins_registry.registry_search_plugins", _fake_search_nonempty
    )

    response = client.get("/registry")
    assert response.status_code == 200
    assert any(p["name"] == "Some Registry Plugin" for p in response.json())


def test_registry_dedups_installed_by_plugin_url(client, just_installed_plugin, monkeypatch):
    """A registry entry sharing an installed plugin's plugin_url is not duplicated."""

    # mock_plugin has no plugin.json, so its manifest.plugin_url defaults to "Unknown".
    async def _search(search=None):
        return [
            PluginManifest(name="Already Installed", plugin_url="Unknown"),
            PluginManifest(name="Fresh From Registry", plugin_url="https://example.com/p"),
        ]

    monkeypatch.setattr(
        "cat.routes.plugins.plugins_registry.registry_search_plugins", _search
    )

    response = client.get("/registry")
    assert response.status_code == 200
    plugins = response.json()

    names = [p["name"] for p in plugins]
    # the installed mock appears once (as installed), annotated active
    mock = next(p for p in plugins if p["name"] == "mock_plugin")
    assert mock["local_info"]["active"] is True
    # the registry twin (same plugin_url) is deduped away
    assert "Already Installed" not in names
    # an unrelated registry plugin still shows
    assert "Fresh From Registry" in names


def test_registry_requires_admin(anon_client):
    response = anon_client.get("/registry")
    assert response.status_code == 403


def test_plugin_install_from_registry(client, monkeypatch):
    # mock the registry download (install_plugin calls it for http origins)
    monkeypatch.setattr(
        "cat.mad_hatter.mad_hatter.registry_download_plugin", _fake_download
    )

    mock_plugin_folder = os.path.join(config.PLUGINS_PATH, "mock_plugin")
    assert not os.path.exists(mock_plugin_folder)

    response = client.post(
        "/registry/install",
        json={"url": "https://mockup_url.com"},
    )
    assert response.status_code == 200, response.text
    # the install endpoint returns the installed plugin's manifest
    assert response.json()["name"] == "mock_plugin"

    # plugin is now installed and active
    response = client.get("/plugins/mock_plugin")
    assert response.status_code == 200
    assert response.json()["id"] == "mock_plugin"
    assert response.json()["active"]

    assert os.path.exists(mock_plugin_folder)
