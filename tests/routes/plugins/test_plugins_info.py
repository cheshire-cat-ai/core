"""GET /plugins and GET /plugins/{id} — the v2 installed-plugins listing.

The response is a flat list of `InstalledPlugin` objects ({id, active, manifest});
there is no `installed`/`registry`/`filters` envelope (registry browsing lives at
`/registry`).
"""


def test_list_plugins_core_only(client, admin_headers):
    """Core-only: no plugins installed, so the list is empty."""
    response = client.get("/plugins", headers=admin_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_list_plugins_with_installed(client, just_installed_plugin, admin_headers):
    response = client.get("/plugins", headers=admin_headers)
    assert response.status_code == 200

    plugins = response.json()
    assert isinstance(plugins, list)

    mock = next(p for p in plugins if p["id"] == "mock_plugin")
    assert isinstance(mock["active"], bool)
    assert mock["active"]
    # manifest is embedded; no plugin.json in the mock, so name == id
    assert mock["manifest"]["name"] == "mock_plugin"


def test_get_plugin_by_id(client, just_installed_plugin, admin_headers):
    response = client.get("/plugins/mock_plugin", headers=admin_headers)
    assert response.status_code == 200

    body = response.json()
    assert body["id"] == "mock_plugin"
    assert isinstance(body["active"], bool)
    assert body["active"]
    assert body["manifest"]["name"] == "mock_plugin"


def test_get_non_existent_plugin(client, admin_headers):
    response = client.get("/plugins/no_plugin", headers=admin_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Plugin not found"
