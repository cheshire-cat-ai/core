
from tests.mocks.mock_plugin.mock_plugin_overrides import MockPluginSettings

def test_get_plugin_settings_non_existent(client, just_installed_plugin):
    non_existent_plugin = "ghost_plugin"
    response = client.get(f"/plugins/settings/{non_existent_plugin}")
    json = response.json()

    assert response.status_code == 404
    assert "not found" in json["detail"]["error"]


# endpoint to get settings and settings schema
def test_get_all_plugin_settings(client, just_installed_plugin):
    response = client.get("/plugins/settings")
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
def test_get_plugin_settings(client, just_installed_plugin):
    response = client.get("/plugins/settings/mock_plugin")
    response_json = response.json()

    assert response.status_code == 200
    assert response_json["name"] == "mock_plugin"
    assert response_json["value"] == {}
    assert response_json["schema"] == MockPluginSettings.model_json_schema()


def test_save_wrong_plugin_settings(client, just_installed_plugin):

    # save settings (empty)
    fake_settings = {}
    response = client.put("/plugins/settings/mock_plugin", json=fake_settings)
    assert response.status_code == 400

    # save settings (wrong schema)
    fake_settings = {"a": "a", "c": 1}
    response = client.put("/plugins/settings/mock_plugin", json=fake_settings)
    assert response.status_code == 400

    # save settings (missing required field)
    fake_settings = {"a": "a"}
    response = client.put("/plugins/settings/mock_plugin", json=fake_settings)
    assert response.status_code == 400

    # check default settings did not change
    response = client.get("/plugins/settings/mock_plugin")
    assert response.status_code == 200
    json = response.json()
    assert json["name"] == "mock_plugin"
    assert json["value"] == {}


def test_save_plugin_settings(client, just_installed_plugin):
    # save settings
    fake_settings = {"a": "a", "b": 1}
    response = client.put("/plugins/settings/mock_plugin", json=fake_settings)

    # check immediate response
    assert response.status_code == 200
    json = response.json()
    assert json["name"] == "mock_plugin"
    assert json["value"] == fake_settings

    # get settings back for this specific plugin
    response = client.get("/plugins/settings/mock_plugin")
    json = response.json()
    assert response.status_code == 200
    assert json["name"] == "mock_plugin"
    assert json["value"] == fake_settings

    # retrieve all plugins settings to check if it was saved in DB
    response = client.get("/plugins/settings")
    json = response.json()
    assert response.status_code == 200
    saved_config = [c for c in json["settings"] if c["name"] == "mock_plugin"]
    assert saved_config[0]["value"] == fake_settings


# core_plugin has no settings and ignores them when saved (for the moment)
def test_core_plugin_settings(client):
    # write a new setting, and then ovewrite it (core_plugin should ignore this)
    for fake_value in ["a", "b"]:
        # save settings
        fake_settings = {"fake_setting": fake_value}
        response = client.put("/plugins/settings/core_plugin", json=fake_settings)

        # check immediate response
        json = response.json()
        assert response.status_code == 200
        assert json["name"] == "core_plugin"
        assert json["value"] == {}

        # get settings back (should be empty as core_plugin does not (yet) accept settings
        response = client.get("/plugins/settings/core_plugin")
        json = response.json()
        assert response.status_code == 200
        assert json["name"] == "core_plugin"
        assert json["value"] == {}
        assert json["schema"] == {}
