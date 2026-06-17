import os

from cat import paths

# NOTE: here we test zip upload install
# install from registry is in `./test_plugins_registry.py`
def test_plugin_install_from_zip(client, just_installed_plugin, admin_headers):
    # during tests, the cat uses a different folder for plugins
    mock_plugin_final_folder = paths.PLUGINS_PATH + "/mock_plugin"

    #### PLUGIN IS ALREADY ACTIVE

    # GET plugin endpoint responds
    response = client.get("/plugins/mock_plugin", headers=admin_headers)
    assert response.status_code == 200
    json = response.json()
    assert json["data"]["id"] == "mock_plugin"
    assert isinstance(json["data"]["active"], bool)
    assert json["data"]["active"]

    # GET plugins endpoint lists the plugin
    response = client.get("/plugins", headers=admin_headers)
    installed_plugins = response.json()["installed"]
    installed_plugins_names = list(map(lambda p: p["id"], installed_plugins))
    assert "mock_plugin" in installed_plugins_names
    # core_plugins and mock_plugin are active
    for p in installed_plugins:
        assert isinstance(p["active"], bool)
        assert p["active"]

    # plugin has been actually extracted in (mock) plugins folder
    assert os.path.exists(mock_plugin_final_folder)


def test_plugin_uninstall(client, just_installed_plugin, admin_headers):
    # during tests, the cat uses a different folder for plugins
    mock_plugin_final_folder = paths.PLUGINS_PATH + "/mock_plugin"

    # remove plugin via endpoint (will delete also plugin folder in mock_plugin_folder)
    response = client.delete("/plugins/mock_plugin", headers=admin_headers)
    assert response.status_code == 200

    # mock_plugin is not installed in the cat (check both via endpoint and filesystem)
    response = client.get("/plugins", headers=admin_headers)
    installed_plugins_names = list(map(lambda p: p["id"], response.json()["installed"]))
    assert "mock_plugin" not in installed_plugins_names
    assert not os.path.exists(
        mock_plugin_final_folder
    )  # plugin folder removed from disk


