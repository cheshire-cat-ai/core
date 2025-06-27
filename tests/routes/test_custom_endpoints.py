import pytest


# endpoints added via mock_plugin (verb, endpoint, payload)
custom_endpoints = [
    ("GET", "/custom/endpoint", None),
    ("GET", "/tests/endpoint", None),
    ("GET", "/tests/crud", None),
    ("POST", "/tests/crud", {"name": "the cat", "description": "it's magic"}),
    ("PUT", "/tests/crud/123", {"name": "the cat", "description": "it's magic"}),
    ("DELETE", "/tests/crud/123", None),
]


def test_custom_endpoint_base(client, just_installed_plugin):

    response = client.get("/custom/endpoint")
    assert response.status_code == 200
    assert response.json()["result"] == "endpoint default prefix"


def test_custom_endpoint_prefix(client, just_installed_plugin):

    response = client.get("/tests/endpoint")
    assert response.status_code == 200
    assert response.json()["result"] == "endpoint prefix tests"


def test_custom_endpoint_get(client, just_installed_plugin):

    response = client.get("/tests/crud")
    assert response.status_code == 200
    assert response.json()["result"] == "ok"
    assert response.json()["user_id"] == "user"


def test_custom_endpoint_post(client, just_installed_plugin):

    payload = {"name": "the cat", "description" : "it's magic"}
    response = client.post("/tests/crud", json=payload)

    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["name"] == "the cat"
    assert response.json()["description"] == "it's magic"


def test_custom_endpoint_put(client, just_installed_plugin):
    payload = {"name": "the cat", "description": "it's magic"}
    response = client.put("/tests/crud/123", json=payload)
    
    assert response.status_code == 200
    assert response.json()["id"] == 123
    assert response.json()["name"] == "the cat"
    assert response.json()["description"] == "it's magic"

def test_custom_endpoint_delete(client, just_installed_plugin):
    response = client.delete("/tests/crud/123")
    
    assert response.status_code == 200
    assert response.json()["result"] == "ok"
    assert response.json()["deleted_id"] == 123


@pytest.mark.parametrize("switch_type", ["deactivation", "uninstall"])
def test_custom_endpoints_on_plugin_deactivation_or_uninstall(
        switch_type, client, just_installed_plugin
    ):

    # custom endpoints are active
    for verb, endpoint, payload in custom_endpoints:
        response = client.request(verb, endpoint, json=payload)
        assert response.status_code == 200

    if switch_type == "deactivation":
        # deactivate plugin
        response = client.put("/plugins/toggle/mock_plugin")
        assert response.status_code == 200
    else:
        # uninstall plugin
        response = client.delete("/plugins/mock_plugin")
        assert response.status_code == 200

    # no more custom endpoints
    for verb, endpoint, payload in custom_endpoints:
        response = client.request(verb, endpoint, json=payload)
        assert response.status_code == 404


@pytest.mark.parametrize("resource", ["PLUGINS", "LLM"])
@pytest.mark.parametrize("permission", ["LIST", "DELETE"])
def test_custom_endpoint_permissions(resource, permission, client, just_installed_plugin):

    # create user with permissions
    response = client.post(
        "/users/",
        json={
            "username": "Alice",
            "password": "Alice",
            "permissions": {resource: [permission]}
        }
    )
    assert response.status_code == 200

    # get jwt for user
    response = client.post("/auth/token", json={"username": "Alice", "password": "Alice"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # use endpoint (requires PLUGINS LIST)
    response = client.get("/tests/crud", headers={"Authorization": f"Bearer {token}"})
    if resource == "PLUGINS" and permission == "LIST":
        assert response.status_code == 200
    else:
        assert response.status_code == 403


def test_custom_endpoint_security(just_installed_plugin, secure_client):

    for verb, endpoint, payload in custom_endpoints:
        response = secure_client.request(verb, endpoint, json=payload)
        if "/endpoint" in endpoint:
            # open endpoints (no StrayCat dependency)
            assert response.status_code == 200
        else:
            # closed endpoints (require StrayCat)
            assert response.status_code == 403

