from uuid import uuid5, NAMESPACE_DNS

import pytest


# The admin user the master API key ("meow") maps to (see services/auths/base).
ADMIN_USER_ID = str(uuid5(NAMESPACE_DNS, "admin"))


# endpoints added via mock_plugin (verb, path, payload), matching mock_endpoint.py
custom_endpoints = [
    ("GET", "/endpoint", None),
    ("GET", "/tests/endpoint", None),
    ("GET", "/tests/crud", None),
    ("POST", "/tests/crud", {"name": "the cat", "description": "it's magic"}),
    ("PUT", "/tests/crud/123", {"name": "the cat", "description": "it's magic"}),
    ("DELETE", "/tests/crud/123", None),
    ("GET", "/tests/role", None),
]


def test_custom_endpoint_base(client, just_installed_plugin):
    response = client.get("/endpoint")
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
    assert response.json()["user_id"] == ADMIN_USER_ID


def test_custom_endpoint_post(client, just_installed_plugin):
    payload = {"name": "the cat", "description": "it's magic"}
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
        response = client.put("/plugins/mock_plugin/toggle")
        assert response.status_code == 200
    else:
        response = client.delete("/plugins/mock_plugin")
        assert response.status_code == 200

    # no more custom endpoints
    for verb, endpoint, payload in custom_endpoints:
        response = client.request(verb, endpoint, json=payload)
        assert response.status_code == 404


def test_custom_endpoint_security(just_installed_plugin, anon_client):
    n_open = 0
    n_protected = 0
    for verb, endpoint, payload in custom_endpoints:
        response = anon_client.request(verb, endpoint, json=payload)
        if "/endpoint" in endpoint:
            # open endpoints (no auth dependency)
            assert response.status_code == 200
            n_open += 1
        else:
            # closed endpoints
            assert response.status_code == 403
            n_protected += 1

    assert n_open == 2
    assert n_protected == 5
