import os
import asyncio
import pytest
import time
import jwt
from tests.utils import send_websocket_message

from cat.env import get_env
from cat.auth.utils import is_jwt, AuthPermission, AuthResource

# TODOAUTH: test token refresh / invalidation / logoff


def test_is_jwt(client):
    assert not is_jwt("not_a_jwt.not_a_jwt.not_a_jwt")

    actual_jwt = jwt.encode(
        {"username": "Alice"},
        get_env("CCAT_JWT_SECRET"),
        algorithm=get_env("CCAT_JWT_ALGORITHM"),
    )
    assert is_jwt(actual_jwt)


def test_refuse_issue_jwt(client):
    creds = {"username": "admin", "password": "wrong"}
    res = client.post("/auth/token", json=creds)

    # wrong credentials
    assert res.status_code == 403
    json = res.json()
    assert json["detail"]["error"] == "Invalid Credentials"


@pytest.mark.asyncio  # to test async functions
async def test_issue_jwt(client):
    creds = {
        "username": "admin",
        "password": "admin",  # TODOAUTH: check custom credentials
    }
    res = client.post("/auth/token", json=creds)

    assert res.status_code == 200

    # did we obtain a JWT?
    res.json()["token_type"] == "bearer"
    received_token = res.json()["access_token"]
    assert is_jwt(received_token)

    # is the JWT correct for core auth handler?
    auth_handler = client.app.state.ccat.core_auth_handler
    user_info = await auth_handler.authorize_user_from_jwt(
        received_token, AuthResource.ADMIN, AuthPermission.WRITE
    )
    assert user_info.user_id == "admin"
    assert user_info.user_data["username"] == "admin"
    assert (
        user_info.user_data["exp"] - time.time() < 60 * 60 * 24
    )  # expires in less than 24 hours

    # manual JWT verification
    try:
        payload = jwt.decode(
            received_token,
            get_env("CCAT_JWT_SECRET"),
            algorithms=[get_env("CCAT_JWT_ALGORITHM")],
        )
        assert payload["username"] == "admin"
        assert (
            payload["exp"] - time.time() < 60 * 60 * 24
        )  # expires in less than 24 hours
    except jwt.exceptions.DecodeError:
        assert False


# test token expiration after successfull login
@pytest.mark.asyncio
async def test_jwt_expiration(client):
    # secure endpoints
    os.environ["CCAT_API_KEY"] = "meow_http"
    # set ultrashort JWT expiration time
    os.environ["CCAT_JWT_EXPIRE_MINUTES"] = "0.05"  # 3 seconds

    # not allowed
    response = client.get("/")
    assert response.status_code == 403
    assert response.json()["detail"]["error"] == "Invalid Credentials"

    # request JWT
    creds = {
        "username": "admin",
        "password": "admin",  # TODOAUTH: check custom credentials
    }
    res = client.post("/auth/token", json=creds)
    assert res.status_code == 200
    token = res.json()["access_token"]

    # allowed via JWT
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/", headers=headers)
    assert response.status_code == 200

    # wait for expiration time
    time.sleep(3)

    # not allowed because JWT expired
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/", headers=headers)
    assert response.status_code == 403
    assert response.json()["detail"]["error"] == "Invalid Credentials"

    # restore default envs
    del os.environ["CCAT_JWT_EXPIRE_MINUTES"]
    del os.environ["CCAT_API_KEY"]
