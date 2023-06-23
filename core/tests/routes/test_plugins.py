import pytest
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





