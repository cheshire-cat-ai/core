import pytest

def test_custom_endpoint_base(client, just_installed_plugin):

    response = client.get("/custom/endpoint")
    assert response.status_code == 200
    assert response.json()["result"] == "endpoint default prefix"


def test_custom_endpoint_prefix(client, just_installed_plugin):

    response = client.get("/tests/endpoint")
    assert response.status_code == 200
    assert response.json()["result"] == "endpoint prefix tests"


def test_custom_endpoint_get(client, just_installed_plugin):

    response = client.get("/tests/get")
    assert response.status_code == 200
    assert response.json()["result"] == "ok"
    assert response.json()["stray_user_id"] == "user"


def test_custom_endpoint_post(client, just_installed_plugin):

    payload = {"name": "the cat", "description" : "it's magic"}
    response = client.post("/tests/post", json=payload)

    assert response.status_code == 200
    assert response.json()["name"] == "the cat"
    assert response.json()["description"] == "it's magic"


@pytest.mark.parametrize("switch_type", ["deactivation", "uninstall"])
def test_custom_endpoints_on_plugin_deactivation_or_uninstall(
        switch_type, client, just_installed_plugin
    ):

    # endpoints added via mock_plugin (verb, endpoint, payload)
    custom_endpoints = [
        ("GET", "/custom/endpoint", None),
        ("GET", "/tests/endpoint", None),
        ("GET", "/tests/get", None),
        ("POST", "/tests/post", {"name": "the cat", "description": "it's magic"}),
    ]

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



