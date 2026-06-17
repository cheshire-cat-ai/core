
from tests.mocks.mock_plugin.mock_plugin_overrides import MockPluginSettings

def test_get_plugin_settings_non_existent(client, just_installed_plugin, admin_headers):
    non_existent_plugin = "ghost_plugin"
    response = client.get(f"/plugins/settings/{non_existent_plugin}", headers=admin_headers)
    json = response.json()

    assert response.status_code == 404
    assert "not found" in json["detail"]


# endpoint to get settings and settings schema
def test_get_all_plugin_settings(client, just_installed_plugin, admin_headers):
    response = client.get("/plugins/settings", headers=admin_headers)
    json = response.json()

    installed_plugins = ["core_plugin", "mock_plugin"]
    
    assert response.status_code == 200
    assert isinstance(json["settings"], list)
    assert len(json["settings"]) == len(installed_plugins)

    for setting in json["settings"]:
        assert setting["name"] in installed_plugins
        if setting["name"] == "core_plugin":
            assert setting["value"] == {}
            assert setting["schema"] == {}
        elif setting["name"] == "mock_plugin":
            assert setting["name"] == "mock_plugin"
            assert setting["value"] == {}
            assert setting["schema"] == MockPluginSettings.model_json_schema()


# endpoint to get settings and settings schema
def test_get_plugin_settings(client, just_installed_plugin, admin_headers):
    response = client.get("/plugins/settings/mock_plugin", headers=admin_headers)
    response_json = response.json()

    assert response.status_code == 200
    assert response_json["name"] == "mock_plugin"
    assert response_json["value"] == {}
    assert response_json["schema"] == MockPluginSettings.model_json_schema()


def test_save_wrong_plugin_settings(client, just_installed_plugin, admin_headers):

    # save settings (empty)
    fake_settings = {}
    response = client.put("/plugins/settings/mock_plugin", headers=admin_headers, json=fake_settings)
    assert response.status_code == 400

    # save settings (wrong schema)
    fake_settings = {"a": "a", "c": 1}
    response = client.put("/plugins/settings/mock_plugin", headers=admin_headers, json=fake_settings)
    assert response.status_code == 400

    # save settings (missing required field)
    fake_settings = {"a": "a"}
    response = client.put("/plugins/settings/mock_plugin", headers=admin_headers, json=fake_settings)
    assert response.status_code == 400

    # check default settings did not change
    response = client.get("/plugins/settings/mock_plugin", headers=admin_headers)
    assert response.status_code == 200
    json = response.json()
    assert json["name"] == "mock_plugin"
    assert json["value"] == {}


def test_save_plugin_settings(client, just_installed_plugin, admin_headers):
    # save settings
    fake_settings = {"a": "a", "b": 1}
    response = client.put("/plugins/settings/mock_plugin", headers=admin_headers, json=fake_settings)

    # check immediate response
    assert response.status_code == 200
    json = response.json()
    assert json["name"] == "mock_plugin"
    assert json["value"] == fake_settings

    # get settings back for this specific plugin
    response = client.get("/plugins/settings/mock_plugin", headers=admin_headers)
    json = response.json()
    assert response.status_code == 200
    assert json["name"] == "mock_plugin"
    assert json["value"] == fake_settings

    # retrieve all plugins settings to check if it was saved in DB
    response = client.get("/plugins/settings", headers=admin_headers)
    json = response.json()
    assert response.status_code == 200
    saved_config = [c for c in json["settings"] if c["name"] == "mock_plugin"]
    assert saved_config[0]["value"] == fake_settings

