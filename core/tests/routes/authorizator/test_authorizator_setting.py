import time
from json import dumps
from fastapi.encoders import jsonable_encoder
from cat.factory.authorizator import get_authorizators_schemas
from tests.utils import get_procedural_memory_contents


def test_get_all_authorizator_settings(client):
    AUTHORIZATOR_SCHEMAS = get_authorizators_schemas()
    response = client.get("/authorizator/settings")
    json = response.json()

    assert response.status_code == 200
    assert type(json["settings"]) == list
    assert len(json["settings"]) == len(AUTHORIZATOR_SCHEMAS)

    for setting in json["settings"]:
        assert setting["name"] in AUTHORIZATOR_SCHEMAS.keys()
        assert setting["value"] == {}
        expected_schema = AUTHORIZATOR_SCHEMAS[setting["name"]]
        assert dumps(jsonable_encoder(expected_schema)) == dumps(setting["schema"])

    # automatically selected authorizator
    assert json["selected_configuration"] == "AuthorizatorNoAuthConfig"


def test_get_authorizator_settings_non_existent(client):

    non_existent_authorizator_name = "AuthorizatorNonExistent"
    response = client.get(f"/authorizator/settings/{non_existent_authorizator_name}")
    json = response.json()

    assert response.status_code == 400
    assert f"{non_existent_authorizator_name} not supported" in json["detail"]["error"]


def test_get_authorizator_settings(client):

    authorizator_name = "AuthorizatorNoAuthConfig"
    response = client.get(f"/authorizator/settings/{authorizator_name}")
    json = response.json()

    assert response.status_code == 200
    assert json["name"] == authorizator_name
    assert json["value"] == {}
    assert json["schema"]["auhrizatorName"] == authorizator_name
    assert json["schema"]["type"] == "object"


def test_upsert_authorizator_settings(client):
    
    # set a different authorizator from default one (same class different size # TODO: have another fake/test authorizator class)
    new_authorizator = "AuthorizatorNoAuthConfig"
    authorizator_config = {}
    response = client.put(f"/authorizator/settings/{new_authorizator}", json=authorizator_config)
    json = response.json()

    # verify success
    assert response.status_code == 200
    assert json["name"] == new_authorizator

    # retrieve all authorizators settings to check if it was saved in DB
    response = client.get("/authorizator/settings")
    json = response.json()
    assert response.status_code == 200
    assert json["selected_configuration"] == new_authorizator
    saved_config = [ c for c in json["settings"] if c["name"] == new_authorizator ]

    # check also specific authorizator endpoint
    response = client.get(f"/authorizator/settings/{new_authorizator}")
    assert response.status_code == 200
    json = response.json()
    assert json["name"] == new_authorizator
    assert json["schema"]["auhrizatorName"] == new_authorizator
