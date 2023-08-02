from tests.utils import get_embedded_tools
from fixture_just_installed_plugin import just_installed_plugin


# endpoint to get settings and settings schema
def test_get_plugin_settings(client, just_installed_plugin):
    
    response = client.get("/plugins/settings/mock_plugin")
    response_json = response.json()

    assert response.status_code == 200
    assert response_json["status"] == "success"
    assert response_json["settings"] == {}
    assert response_json["schema"]['properties'] == {}
    assert response_json["schema"]['title'] == 'BaseModel'
    assert response_json["schema"]['type'] == 'object'


# endpoint to save settings
def test_save_plugin_settings(client, just_installed_plugin):

    # write a new setting, and then ovewrite it 
    for fake_value in ["a", "b"]:
        # save settings
        fake_settings = {"fake_setting": fake_value}
        response = client.put("/plugins/settings/mock_plugin", json=fake_settings)
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["status"] == "success"
        assert response_json["settings"]["fake_setting"] == fake_value

        # get settings back
        response = client.get("/plugins/settings/mock_plugin")
        response_json = response.json()
        assert response.status_code == 200
        assert response_json["status"] == "success"
        assert response_json["settings"]["fake_setting"] == fake_value


# core_plugin has no settings (for the moment)
def test_core_plugin_settings(client):

    # write a new setting, and then ovewrite it (core_plugin should ignore this)
    for fake_value in ["a", "b"]:
        # save settings
        fake_settings = {"fake_setting": fake_value}
        response = client.put("/plugins/settings/core_plugin", json=fake_settings)
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["status"] == "success"

        # get settings back
        response = client.get("/plugins/settings/core_plugin")
        response_json = response.json()
        assert response.status_code == 200
        assert response_json["status"] == "success"
        assert response_json["schema"]['properties'] == {}
        assert response_json["schema"]['title'] == 'CorePluginSettings'
        assert response_json["schema"]['type'] == 'object'
        assert response_json["settings"] == {}