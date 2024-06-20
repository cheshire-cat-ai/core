
import os
import asyncio
import pytest
import time
import jwt
from tests.utils import send_websocket_message

from cat.env import get_env
from cat.auth.utils import is_jwt, AuthPermission, AuthResource


def test_is_jwt(client):

    assert not is_jwt("not_a_jwt.not_a_jwt.not_a_jwt")

    actual_jwt = jwt.encode(
        {"username": "Alice"},
        get_env("CCAT_JWT_SECRET"),
        algorithm=get_env("CCAT_JWT_ALGORITHM")
    )
    assert is_jwt(actual_jwt)


@pytest.mark.asyncio # to test async functions
async def test_issue_jwt(client):

    creds = {
        "username": "admin",
        "password": "admin" # TODOAUTH: check custom credentials
    }
    res = client.post("/auth/token", data=creds)

    assert res.status_code == 200

    # did we obtain a JWT?
    res.json()["token_type"] == "bearer"
    received_token = res.json()["access_token"]
    assert is_jwt(received_token)

    # is the JWT correct for core auth handler?
    auth_handler = client.app.state.ccat.core_auth_handler
    user_info = await auth_handler.authorize_user_from_token(
        received_token, AuthResource.ADMIN, AuthPermission.WRITE
    )
    assert user_info.user_id == "admin"
    assert user_info.user_data["username"] == "admin"
    assert user_info.user_data["exp"] - time.time() < 30 * 60 # expires in less than 30 minutes
    
    # manual JWT verification
    try:
        payload = jwt.decode(
            received_token,
            get_env("CCAT_JWT_SECRET"),
            algorithms=[get_env("CCAT_JWT_ALGORITHM")]
        )
        assert payload["username"] == "admin"
        assert payload["exp"] - time.time() < 30 * 60
    except jwt.exceptions.DecodeError:
        assert False


def test_refuse_issue_jwt(client):

    creds = {
        "username": "admin",
        "password": "wrong"
    }
    res = client.post("/auth/token", data=creds)

    # wrong credentials
    assert res.status_code == 403
    json = res.json()
    assert json["detail"]["error"] == "Invalid Credentials"


# TODOAUTH: test token expiration after successfull login
# TODOAUTH: test token invalidation / logoff