import os
import pytest
from tests.utils import send_websocket_message


@pytest.fixture
def secure_client(client):
    # set ENV variables
    os.environ["CCAT_API_KEY"] = "meow_http"
    os.environ["CCAT_API_KEY_WS"] = "meow_ws"
    yield client
    del os.environ["CCAT_API_KEY"]
    del os.environ["CCAT_API_KEY_WS"]


def test_api_key_http(secure_client):

    # forbid access if no CCAT_API_KEY is provided
    response = secure_client.get("/")
    assert response.status_code == 403
    assert response.json()["detail"]["error"] == "Invalid Credentials"

    # forbid access if CCAT_API_KEY is wrong
    headers = {
        "access_token": "wrong"
    }
    response = secure_client.get("/", headers=headers)
    assert response.status_code == 403
    assert response.json()["detail"]["error"] == "Invalid Credentials"

    # allow access if CCAT_API_KEY is right
    headers = {
        "access_token": "meow_http"
    }
    response = secure_client.get("/", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "We're all mad here, dear!"


def test_api_key_ws(secure_client):

    mex = {"text": "Where do I go?"}

    # forbid access if no CCAT_API_KEY_WS is provided
    with pytest.raises(Exception) as e_info:
        res = send_websocket_message(mex, secure_client)
    assert str(e_info.type.__name__) == 'WebSocketDisconnect'

    # forbid access if CCAT_API_KEY_WS is wrong
    query_params = {
        "access_token": "wrong"
    }
    with pytest.raises(Exception) as e_info:
        res = send_websocket_message(mex, secure_client, query_params=query_params)
    assert str(e_info.type.__name__) == 'WebSocketDisconnect'
    
    # allow access if CCAT_API_KEY_WS is right
    query_params = {
        "access_token": "meow_ws"
    }
    res = send_websocket_message(mex, secure_client, query_params=query_params)
    assert "You did not configure" in res["content"]
    



