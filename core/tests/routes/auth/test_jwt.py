
import os
import pytest
from tests.utils import send_websocket_message


#@pytest.fixture
#def secure_client(client):
    # set CCAT_API_KEY
#    os.environ["CCAT_API_KEY"] = "meow"
#    yield client
#    del os.environ["CCAT_API_KEY"]


def test_issue_jwt(client):

    creds = {
        "user_name": "admin",
        "password": "admin" # TODOAUTH: check custom credentials
    }
    res = client.post("/auth/token", json=creds)

    assert res.status_code == 200
    json = res.json()
    print(json)
    assert json["token_type"] == "bearer"
    assert type(json["access_token"]) == str
    assert len(json["access_token"]) > 100


def test_refuse_issue_jwt(client):

    creds = {
        "user_name": "admin",
        "password": "wrong"
    }
    res = client.post("/auth/token", json=creds)

    assert res.status_code == 401
    json = res.json()
    assert json["detail"]["error"] == "Invalid Credentials"
