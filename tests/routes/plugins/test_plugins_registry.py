"""Registry routes (core capability): browse `/registry` and install via
`POST /registry/install`.

Registry access is network-bound, so both the search (list) and the download are
mocked — these tests exercise core's install plumbing, not the live registry.
"""

import os

import pytest

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


def test_list_registry_plugins_empty(client, admin_headers, monkeypatch):
    """With an empty registry, GET /registry returns an empty list (core-only)."""
    monkeypatch.setattr(
        "cat.routes.plugins.plugins_registry.registry_search_plugins", _fake_search_empty
    )

    response = client.get("/registry", headers=admin_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.xfail(
    reason=(
        "FROZEN-CODE BUG: plugins_registry.py:28 reads `p.id` on a PluginManifest, "
        "but PluginManifest has no `id` field and registry_search_plugins' extra "
        "`id` key is dropped by pydantic — GET /registry 500s on any non-empty "
        "registry. Reported to maintainer; do not fix src under the freeze."
    ),
    strict=True,
)
def test_list_registry_plugins_nonempty(client, admin_headers, monkeypatch):
    monkeypatch.setattr(
        "cat.routes.plugins.plugins_registry.registry_search_plugins", _fake_search_nonempty
    )

    response = client.get("/registry", headers=admin_headers)
    assert response.status_code == 200
    assert any(p["name"] == "Some Registry Plugin" for p in response.json())


def test_registry_requires_admin(client):
    response = client.get("/registry")
    assert response.status_code == 403


def test_plugin_install_from_registry(client, admin_headers, monkeypatch):
    # mock the registry download (install_plugin calls it for http origins)
    monkeypatch.setattr(
        "cat.mad_hatter.mad_hatter.registry_download_plugin", _fake_download
    )

    mock_plugin_folder = os.path.join(config.PLUGINS_PATH, "mock_plugin")
    assert not os.path.exists(mock_plugin_folder)

    response = client.post(
        "/registry/install",
        headers=admin_headers,
        json={"url": "https://mockup_url.com"},
    )
    assert response.status_code == 200, response.text
    # the install endpoint returns the installed plugin's manifest
    assert response.json()["name"] == "mock_plugin"

    # plugin is now installed and active
    response = client.get("/plugins/mock_plugin", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["id"] == "mock_plugin"
    assert response.json()["active"]

    assert os.path.exists(mock_plugin_folder)
