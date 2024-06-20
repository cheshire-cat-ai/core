
import os
import asyncio
import pytest
import time
from tests.utils import send_websocket_message

from cat.auth.utils import is_jwt

#@pytest.fixture
#def secure_client(client):
    # set CCAT_API_KEY
#    os.environ["CCAT_API_KEY"] = "meow"
#    yield client
#    del os.environ["CCAT_API_KEY"]


def test_is_jwt(client):

    # TODOAUTH: test is_jwt function
    assert True


@pytest.mark.asyncio # to test async functions
async def test_issue_jwt(client):

    creds = {
        "username": "admin",
        "password": "admin" # TODOAUTH: check custom credentials
    }
    res = client.post("/auth/token", data=creds)

    assert res.status_code == 200

    # we expect to be redirected to the admin after login
    # TODOAUTH what happens when M2M
    expected_redirect_url = "http://testserver/admin/?access_token="
    assert str(res.url).startswith(expected_redirect_url)

    # did we obtain a JWT?
    received_token = str(res.url).replace(expected_redirect_url, "")
    assert is_jwt(received_token)

    # is the JWT correct?
    auth_handler = client.app.state.ccat.auth_handler
    user_info = await auth_handler.get_user_info_from_token(received_token)
    assert user_info.user_id == "admin"
    assert user_info.user_data["username"] == "admin"
    assert user_info.user_data["exp"] - time.time() < 30 * 60 # expires in less than 30 minutes
    # TODOAUTH roles and permissions

    # TODOAUTH: in a machine2machine setting, we expect the token to be directly returned
    #assert json["token_type"] == "bearer"
    #assert type(json["access_token"]) == str
    #assert len(json["access_token"]) > 100


def test_refuse_issue_jwt(client):

    creds = {
        "username": "admin",
        "password": "wrong"
    }
    res = client.post("/auth/token", data=creds)

    # we should end up on the identity provider login page, no token
    assert res.status_code == 200
    expected_redirect_url = "http://testserver/auth/core_login"
    assert str(res.url) == expected_redirect_url

    # TODOAUTH: what happens when machine2machine
    #json = res.json()
    #assert json["detail"]["error"] == "Invalid Credentials"


# TODOAUTH: test /auth/token endpoint (it is called from the identity provider)
# TODOAUTH: token expiration
# TODOAUTH: token invalidation / logoff