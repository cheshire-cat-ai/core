import os
import time
import pytest
import shutil
from tests.utils import key_in_json, create_mock_plugin_zip


# utility to retrieve embedded tools from endpoint
def get_embedded_tools(client):
    params = {
        "text": "random"
    }
    response = client.get(f"/memory/recall/", params=params)
    json = response.json()
    return json["vectors"]["collections"]["procedural"]
    

@pytest.mark.parametrize("key", ["status", "results", "installed", "registry"])
def test_list_plugins(client, key):
    # Act
    response = client.get("/plugins")

    response_json = response.json()

    # Assert
    assert response.status_code == 200
    assert key_in_json(key, response_json)


@pytest.mark.parametrize("keys", ["status", "data"])
def test_get_plugin_id(client, keys):
    # Act
    response = client.get("/plugins/core_plugin")

    response_json = response.json()

    assert key_in_json(keys, response_json)
    assert response_json["status"] == "success"
    assert response_json["data"] is not None


# TODO: these test cases should be splitted in different test functions, with apppropriate setup/teardown
# TODO: mock the plugin folder, otherwise uploading a plugin from here will make the production app reload
def test_plugin_zip_upload(client):

    # mock_plugin is not installed in the cat (check both via endpoint and filesystem)
    response = client.get("/plugins")
    installed_plugins_names = list(map(lambda p: p["id"], response.json()["installed"]))
    assert "mock_plugin" not in installed_plugins_names
    assert not os.path.exists("/app/cat/plugins/mock_plugin")

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

    # wait for mad hatter discovery and tool embedding
    time.sleep(5)

    # GET plugins endpoint lists the plugin
    response = client.get("/plugins")
    installed_plugins_names = list(map(lambda p: p["id"], response.json()["installed"]))
    print(installed_plugins_names)
    assert "mock_plugin" in installed_plugins_names
    # plugin has been actually extracted in plugins folder
    assert os.path.exists("/app/cat/plugins/mock_plugin")

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
    assert not os.path.exists("/app/cat/plugins/mock_plugin")

    # plugin tool disappeared
    tools = get_embedded_tools(client)
    tool_names = list(map(lambda t: t["metadata"]["name"], tools))
    assert "random_idea" not in tool_names
    
    os.remove(zip_path) # delete zip from tests folder


