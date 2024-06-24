import pytest
from tests.utils import send_websocket_message

# these tests use the secure_client fixture defined in conftest.py
# the fixture sets both CCAT_API_KEY and CCAT_API_KEY_WS to "meow_http" and "meow_ws" respectively

@pytest.mark.parametrize("header_name", ["Authorization", "access_token"])
def test_api_key_http(secure_client, header_name):
    # forbid access if no CCAT_API_KEY is provided
    response = secure_client.get("/")
    assert response.status_code == 403
    assert response.json()["detail"]["error"] == "Invalid Credentials"

    # to add "Bearer: " whe using Authorization header
    key_prefix = ""
    if header_name == "Authorization":
        key_prefix = "Bearer "

    # forbid access if CCAT_API_KEY is wrong
    headers = {header_name: f"{key_prefix}wrong"}
    response = secure_client.get("/", headers=headers)
    assert response.status_code == 403
    assert response.json()["detail"]["error"] == "Invalid Credentials"

    # http access not allowed if CCAT_API_KEY_WS is passed
    headers = {header_name: f"{key_prefix}meow_ws"}
    response = secure_client.get("/", headers=headers)
    assert response.status_code == 403
    assert response.json()["detail"]["error"] == "Invalid Credentials"

    # allow access if CCAT_API_KEY is right
    headers = {header_name: f"{key_prefix}meow_http"}
    response = secure_client.get("/", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "We're all mad here, dear!"


def test_api_key_ws(secure_client):
    mex = {"text": "Where do I go?"}

    # forbid access if no CCAT_API_KEY_WS is provided
    with pytest.raises(Exception) as e_info:
        res = send_websocket_message(mex, secure_client)
    assert str(e_info.type.__name__) == "WebSocketDisconnect"

    # forbid access if CCAT_API_KEY_WS is wrong
    query_params = {"token": "wrong"}
    with pytest.raises(Exception) as e_info:
        res = send_websocket_message(mex, secure_client, query_params=query_params)
    assert str(e_info.type.__name__) == "WebSocketDisconnect"

    # TODOAUTH: is there a more secure way to pass the token over websocket?
    query_params = {"token": "meow_ws"}
    res = send_websocket_message(mex, secure_client, query_params=query_params)
    assert "You did not configure" in res["content"]
