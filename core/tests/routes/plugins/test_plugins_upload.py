import os
import time
import pytest
import shutil
from tests.utils import create_mock_plugin_zip, get_embedded_tools


# TODO: these test cases should be splitted in different test functions, with apppropriate setup/teardown
def test_plugin_zip_upload(client):

    # during tests, the cat uses a different folder for plugins
    mock_plugin_final_folder = "tests/mocks/mock_plugin_folder/mock_plugin"

    # mock_plugin is not installed in the cat (check both via endpoint and filesystem)
    response = client.get("/plugins")
    installed_plugins_names = list(map(lambda p: p["id"], response.json()["installed"]))
    assert "mock_plugin" not in installed_plugins_names
    assert not os.path.exists(mock_plugin_final_folder)

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

    #### PLUGIN IS NOT YET ACTIVE

    # GET plugins endpoint lists the plugin
    response = client.get("/plugins")
    installed_plugins_names = list(map(lambda p: p["id"], response.json()["installed"]))
    print(installed_plugins_names)
    assert "mock_plugin" in installed_plugins_names
    # plugin has been actually extracted in (mock) plugins folder
    assert os.path.exists(mock_plugin_final_folder)

    # new tool has not been embedded
    tools = get_embedded_tools(client)
    tool_names = list(map(lambda t: t["metadata"]["name"], tools))
    assert "random_idea" not in tool_names


    #### ACTIVATE PLUGIN

    response = client.put("/plugins/toggle/mock_plugin")
    assert response.status_code == 200


    #### PLUGIN IS NOW ACTIVE

    # check whether new tools have been embedded
    tools = get_embedded_tools(client)
    tool_names = list(map(lambda t: t["metadata"]["name"], tools))
    assert "random_idea" in tool_names

    # remove plugin via endpoint (will delete also folder in cat/plugins)
    response = client.delete("/plugins/mock_plugin")
    assert response.status_code == 200

    # mock_plugin is not installed in the cat (check both via endpoint and filesystem)
    response = client.get("/plugins")
    installed_plugins_names = list(map(lambda p: p["id"], response.json()["installed"]))
    assert "mock_plugin" not in installed_plugins_names
    assert not os.path.exists(mock_plugin_final_folder)

    # plugin tool disappeared
    tools = get_embedded_tools(client)
    tool_names = list(map(lambda t: t["metadata"]["name"], tools))
    assert "random_idea" not in tool_names
    
    os.remove(zip_path) # delete zip from tests folder


