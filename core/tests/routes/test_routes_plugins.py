import os
import pytest
import shutil
from tests.utils import key_in_json


@pytest.mark.parametrize("key", ["status", "results", "installed", "registry"])
def test_list_plugins(client, key):
    # Act
    response = client.get(
        "/plugins")

    response_json = response.json()

    # Assert
    assert response.status_code == 200
    assert key_in_json(key, response_json)


@pytest.mark.parametrize("keys", ["status", "data"])
def test_get_plugin_id(client, keys):
    # Act
    response = client.get(
        f"/plugins/core_plugin")

    response_json = response.json()

    assert key_in_json(keys, response_json)
    assert response_json["status"] == "success"
    assert response_json["data"] is not None


# TODO: these test cases should be splitted in different test functions, with apppropriate setup/teardown
def test_plugin_zip_upload(client):

    # mock_plugin is not installed in the cat (check both via endpoint and filesystem)
    response = client.get("/plugins")
    installed_plugins_names = list(map(lambda p: p["id"], response.json()["installed"]))
    assert "mock_plugin" not in installed_plugins_names
    assert not os.path.exists("/app/cat/plugins/mock_plugin")

    # create zip file with a plugin
    zip_file_name = "mock_plugin.zip"
    zip_path = f"tests/mocks/{zip_file_name}"
    shutil.make_archive(
        zip_path.replace(".zip", ""),
        "zip",
        root_dir="tests/mocks/",
        base_dir="mock_plugin"
    )

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
    assert response.json()["filename"] == zip_file_name

    # GET plugins endpoint lists the plugin
    response = client.get("/plugins")
    installed_plugins_names = list(map(lambda p: p["id"], response.json()["installed"]))
    assert "mock_plugin" in installed_plugins_names
    # plugin has been actually extracted in plugins folder
    assert os.path.exists("/app/cat/plugins/mock_plugin")

    # TODO: check whether new tools have been embedded

    # remove plugin via endpoint (will delete also folder in cat/plugins)
    response = client.delete("/plugins/mock_plugin")
    assert response.status_code == 200

    # mock_plugin is not installed in the cat (check both via endpoint and filesystem)
    response = client.get("/plugins")
    installed_plugins_names = list(map(lambda p: p["id"], response.json()["installed"]))
    assert "mock_plugin" not in installed_plugins_names
    assert not os.path.exists("/app/cat/plugins/mock_plugin")

    os.remove(zip_path) # delete zip from tests folder

