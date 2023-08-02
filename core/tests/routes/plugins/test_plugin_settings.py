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
    assert response_json["schema"]['title'] == 'BasePluginSettings'
    assert response_json["schema"]['type'] == 'object'


# endpoint to save settings
def test_save_plugin_settings(client, just_installed_plugin):

    # save settings
    fake_settings = {"fake_setting": 42}
    response = client.put("/plugins/settings/mock_plugin", json=fake_settings)
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["status"] == "success"
    assert response_json["settings"]["fake_setting"] == fake_settings["fake_setting"]

    # get settings back
    response = client.get("/plugins/settings/mock_plugin")
    response_json = response.json()
    assert response.status_code == 200
    assert response_json["status"] == "success"
    assert response_json["settings"]["fake_setting"] == fake_settings["fake_setting"]


    