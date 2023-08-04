import os
import time
import pytest
import shutil
from tests.utils import key_in_json


@pytest.mark.parametrize("key", ["status", "results", "installed", "registry"])
def test_list_plugins(client, key):
    # Act
    response = client.get("/plugins")

    response_json = response.json()

    # Assert
    assert response.status_code == 200
    assert key_in_json(key, response_json)
    assert response_json["installed"][0]["id"] == "core_plugin"
    assert response_json["installed"][0]["active"] == True


@pytest.mark.parametrize("keys", ["status", "data"])
def test_get_plugin_id(client, keys):
    # Act
    response = client.get("/plugins/core_plugin")

    response_json = response.json()

    assert key_in_json(keys, response_json)
    assert response_json["status"] == "success"
    assert response_json["data"] is not None
    assert response_json["data"]["id"] == "core_plugin"
    assert response_json["data"]["active"] == True


def test_get_non_existent_plugin(client):
    
    response = client.get("/plugins/no_plugin")
    response_json = response.json()

    assert response.status_code == 404
    assert response_json["detail"]["error"] == "Plugin not found"

