import os
import pytest
import time
import jwt

from cat.env import get_env
from cat.auth.permissions import AuthPermission, AuthResource
from cat.auth.auth_utils import is_jwt

from tests.utils import send_websocket_message

# TODOAUTH: test token refresh / invalidation / logoff


def test_is_jwt(client):
    assert not is_jwt("not_a_jwt.not_a_jwt.not_a_jwt")

    actual_jwt = jwt.encode(
        {"username": "Alice"},
        "some_secret",
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
        "password": "admin"
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
        received_token, AuthResource.LLM, AuthPermission.WRITE
    )
    assert len(user_info.id) == 36 and len(user_info.id.split("-")) == 5 # uuid4
    assert user_info.name == "admin"

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


@pytest.mark.asyncio
async def test_issue_jwt_for_new_user(client):

    # create new user
    creds = {
        "username": "Alice",
        "password": "Alice",
    }

    # we sohuld not obtain a JWT for this user
    # because it does not exist
    res = client.post("/auth/token", json=creds)
    assert res.status_code == 403
    assert res.json()["detail"]["error"] == "Invalid Credentials"

    # let's create the user
    res = client.post("/users", json=creds)
    assert res.status_code == 200

    # now we should get a JWT
    res = client.post("/auth/token", json=creds)
    assert res.status_code == 200

    # did we obtain a JWT?
    res.json()["token_type"] == "bearer"
    received_token = res.json()["access_token"]
    assert is_jwt(received_token)


# test token expiration after successfull login
# NOTE: here we are using the secure_client fixture (see conftest.py)
def test_jwt_expiration(secure_client):

    # set ultrashort JWT expiration time
    os.environ["CCAT_JWT_EXPIRE_MINUTES"] = "0.05"  # 3 seconds

    # not allowed
    response = secure_client.get("/")
    assert response.status_code == 403
    assert response.json()["detail"]["error"] == "Invalid Credentials"

    # request JWT
    creds = {
        "username": "admin",
        "password": "admin",  # TODOAUTH: check custom credentials
    }
    res = secure_client.post("/auth/token", json=creds)
    assert res.status_code == 200
    token = res.json()["access_token"]

    # allowed via JWT
    headers = {"Authorization": f"Bearer {token}"}
    response = secure_client.get("/", headers=headers)
    assert response.status_code == 200

    # wait for expiration time
    time.sleep(3)

    # not allowed because JWT expired
    headers = {"Authorization": f"Bearer {token}"}
    response = secure_client.get("/", headers=headers)
    assert response.status_code == 403
    assert response.json()["detail"]["error"] == "Invalid Credentials"

    # restore default env
    del os.environ["CCAT_JWT_EXPIRE_MINUTES"]


# test ws and http endpoints can get user_id from JWT
# NOTE: here we are using the secure_client fixture (see conftest.py)
def test_jwt_imposes_user_id(secure_client):

    # not allowed
    response = secure_client.get("/")
    assert response.status_code == 403
    assert response.json()["detail"]["error"] == "Invalid Credentials"

    # request JWT
    creds = {
        "username": "admin", # TODOAUTH: use another user?
        "password": "admin",
    }
    res = secure_client.post("/auth/token", json=creds)
    assert res.status_code == 200
    token = res.json()["access_token"]

    # we will send this message both via http and ws, having the user_id carried by the JWT
    message = {
        "text": "hey"
    }

    # send user specific message via http
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = secure_client.post("/message", headers=headers, json=message)
    assert response.status_code == 200

    # send user specific request via ws
    query_params = {"token": token}
    res = send_websocket_message(message, secure_client, query_params=query_params)

    # we now recall episodic memories from the user, there should be two of them, both by admin
    params = {"text": "hey"}
    response = secure_client.get("/memory/recall/", headers=headers, params=params)
    json = response.json()
    assert response.status_code == 200
    episodic_memories = json["vectors"]["collections"]["episodic"]
    assert len(episodic_memories) == 2
    for em in episodic_memories:
        assert em["metadata"]["source"] == "admin"
        assert em["page_content"] == "hey"


# test that a JWT signed knowing the secret, passes
def test_jwt_self_signature_passes_on_unsecure_client(client):

    # get list of users (we need the ids)
    response = client.get("/users")
    users = response.json()

    for user in users:

        # create a self signed JWT using the default secret              
        token = jwt.encode(
            {"sub": user["id"], "username": user["username"]},
            "secret",
            algorithm=get_env("CCAT_JWT_ALGORITHM"),
        )

        message = { "text": "hey" }

        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = client.post("/message", headers=headers, json=message)
        assert response.status_code == 200
        assert "You did not configure" in response.json()["content"]

        params = {"token": token}
        response = send_websocket_message(message, client, query_params=params)
        assert "You did not configure" in response["content"]


# test that a JWT signed with the wrong secret is not accepted
def test_jwt_self_signature_fails_on_secure_client(secure_client):

    # get list of users (we need the ids)
    response = secure_client.get(
        "/users",
        headers={
            "Authorization": "Bearer meow_http"
        })
    users = response.json()

    for user in users:

        # create a self signed JWT using the default secret              
        token = jwt.encode(
            {"sub": user["id"], "username": user["username"]},
            "secret",
            algorithm=get_env("CCAT_JWT_ALGORITHM"),
        )

        message = { "text": "hey" }

        # not allowed because CCAT_JWT_SECRET for secure_client is `meow_jwt`
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = secure_client.post("/message", headers=headers, json=message)
        assert response.status_code == 403

        # not allowed because CCAT_JWT_SECRET for secure_client is `meow_jwt`
        params = {"token": token}
        with pytest.raises(Exception) as e_info:
            send_websocket_message(message, secure_client, query_params=params)
            assert str(e_info.type.__name__) == "WebSocketDisconnect"



    
    
