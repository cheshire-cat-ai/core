import os
import pytest
from tests.utils import send_websocket_message

@pytest.fixture
def secure_client(client):
    # set CCAT_API_KEY
    os.environ["CCAT_API_KEY"] = "meow"
    yield client
    del os.environ["CCAT_API_KEY"]


def test_api_key_http(secure_client):

    # forbid access if no CCAT_API_KEY is provided
    response = secure_client.get("/")
    assert response.status_code == 403
    assert response.json()["detail"]["error"] == "Invalid API Key"

    # forbid access if CCAT_API_KEY is wrong
    headers = {
        "access_token": "wrong"
    }
    response = secure_client.get("/", headers=headers)
    assert response.status_code == 403
    assert response.json()["detail"]["error"] == "Invalid API Key"

    # allow access if CCAT_API_KEY is right
    headers = {
        "access_token": "meow"
    }
    response = secure_client.get("/", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "We're all mad here, dear!"


def test_api_key_ws(secure_client):

    # TODO: websocket is currently open
    # send websocket message
    mex = {"text": "Where do I go?"}
    res = send_websocket_message(mex, secure_client)
    assert "You did not configure" in res["content"]
