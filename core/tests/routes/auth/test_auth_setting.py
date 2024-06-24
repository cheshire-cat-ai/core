from json import dumps
from fastapi.encoders import jsonable_encoder
from cat.factory.auth_handler import get_auth_handlers_schemas


def test_get_all_auth_handler_settings(client):
    AUTH_HANDLER_SCHEMAS = get_auth_handlers_schemas()
    response = client.get("/auth_handler/settings")
    json = response.json()

    assert response.status_code == 200
    assert isinstance(json["settings"], list)
    assert len(json["settings"]) == len(AUTH_HANDLER_SCHEMAS)

    for setting in json["settings"]:
        assert setting["name"] in AUTH_HANDLER_SCHEMAS.keys()
        assert setting["value"] == {}
        expected_schema = AUTH_HANDLER_SCHEMAS[setting["name"]]
        assert dumps(jsonable_encoder(expected_schema)) == dumps(setting["schema"])

    # automatically selected auth_handler
    assert json["selected_configuration"] == "CoreOnlyAuthConfig"


def test_get_auth_handler_settings_non_existent(client):
    non_existent_auth_handler_name = "AuthHandlerNonExistent"
    response = client.get(f"/auth_handler/settings/{non_existent_auth_handler_name}")
    json = response.json()

    assert response.status_code == 400
    assert f"{non_existent_auth_handler_name} not supported" in json["detail"]["error"]


# TODOAUTH: have at least another auth_handler class to test
"""
def test_get_auth_handler_settings(client):

    auth_handler_name = "AuthEnvironmentVariablesConfig"
    response = client.get(f"/auth_handler/settings/{auth_handler_name}")
    json = response.json()

    assert response.status_code == 200
    assert json["name"] == auth_handler_name
    assert json["value"] == {}
    assert json["schema"]["auhrizatorName"] == auth_handler_name
    assert json["schema"]["type"] == "object"


def test_upsert_auth_handler_settings(client):

    # set a different auth_handler from default one (same class different size # TODO: have another fake/test auth_handler class)
    new_auth_handler = "AuthApiKeyConfig"
    auth_handler_config = {
        "api_key_http": "meow_http",
        "api_key_ws": "meow_ws",
    }
    response = client.put(f"/auth_handler/settings/{new_auth_handler}", json=auth_handler_config)
    json = response.json()

    # verify success
    assert response.status_code == 200
    assert json["name"] == new_auth_handler

    # Retrieve all auth_handlers settings to check if it was saved in DB

    ## We are now forced to use api_key, otherwise we don't get in
    response = client.get("/auth_handler/settings")
    json = response.json()
    assert response.status_code == 403
    assert response.json()["detail"]["error"] == "Invalid Credentials"

    ## let's use the configured api_key for http
    headers = {
        "access_token": "meow_http"
    }
    response = client.get("/auth_handler/settings", headers=headers)
    json = response.json()
    assert response.status_code == 200
    assert json["selected_configuration"] == new_auth_handler
    saved_config = [ c for c in json["settings"] if c["name"] == new_auth_handler ]

    ## check also specific auth_handler endpoint
    response = client.get(f"/auth_handler/settings/{new_auth_handler}", headers=headers)
    assert response.status_code == 200
    json = response.json()
    assert json["name"] == new_auth_handler
    assert json["schema"]["auhrizatorName"] == new_auth_handler
"""
