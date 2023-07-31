import time
import os
import pytest
from tests.utils import create_mock_plugin_zip, get_embedded_tools


# this fixture wraps any test function having `just_installed_plugin` as an argument
@pytest.fixture()
def just_installed_plugin(client):

    ### executed before each test function

    # create zip file with a plugin
    zip_path = create_mock_plugin_zip()
    zip_file_name = zip_path.split("/")[-1] # mock_plugin.zip in tests/mocks folder

    # upload plugin via endpoint
    with open(zip_path, "rb") as f:
        response = client.post(
            "/plugins/upload/",
            files={
                "file": (zip_file_name, f, "application/zip")
            }
        )

    # request was processed
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["filename"] == zip_file_name

    ### each test function below is run here
    yield
    ###

    ### executed after each test function
    # delete zip from tests folder
    os.remove(zip_path)
    # remove plugin via endpoint (will delete also plugin folder in mock_plugin_folder)
    response = client.delete("/plugins/mock_plugin")
    assert response.status_code == 200


def test_toggle_non_existent_plugin(client, just_installed_plugin):
    
    response = client.put("/plugins/toggle/no_plugin")
    response_json = response.json()

    assert response.status_code == 404
    assert response_json["detail"]["error"] == "Plugin not found"


def test_toggle_active_plugin(client, just_installed_plugin):

    # GET plugins endpoint lists the plugin
    response = client.get("/plugins")
    installed_plugins_names = list(map(lambda p: p["id"], response.json()["installed"]))
    print(installed_plugins_names)
    assert "mock_plugin" in installed_plugins_names
    
    # check whether new tools have been embedded
    tools = get_embedded_tools(client)
    tool_names = list(map(lambda t: t["metadata"]["name"], tools))
    assert "random_idea" in tool_names
    

def test_toggle_inactive_plugin(client, just_installed_plugin):
    
    # TODO
    pass
