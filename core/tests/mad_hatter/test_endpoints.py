from cat.mad_hatter.decorators import CustomEndpoint

def test_endpoints_discovery(mad_hatter_with_mock_plugin):

    mock_plugin_endpoints = mad_hatter_with_mock_plugin.plugins["mock_plugin"].endpoints

    assert len(mock_plugin_endpoints) == 4

    for h in mock_plugin_endpoints:
        assert isinstance(h, CustomEndpoint)
        assert h.plugin_id == "mock_plugin"

        if h.name == "/custom-endpoints/endpoint":
            assert h.tags == ["Custom Endpoints"]

        if h.name == "/custom-endpoints/tests":
            assert h.tags == ["Tests"]


def test_endpoint_decorator(client, mad_hatter_with_mock_plugin):

    response = client.get("/custom-endpoints/endpoint")

    assert response.status_code == 200
    
    assert response.json()["result"] == "endpoint default prefix"


def test_endpoint_decorator_prefix(client, mad_hatter_with_mock_plugin):

    response = client.get("/tests/endpoint")

    assert response.status_code == 200
    
    assert response.json()["result"] == "endpoint prefix tests"


def test_get_endpoint(client, mad_hatter_with_mock_plugin):

    response = client.get("/tests/get")

    assert response.status_code == 200
    
    assert response.json()["result"] == "ok"
    assert response.json()["stray_user_id"] == "user"


def test_post_endpoint(client, mad_hatter_with_mock_plugin):

    payload = {"name": "the cat", "description" : "it's magic"}
    response = client.post("/tests/post", json=payload)

    assert response.status_code == 200

    assert response.json()["name"] == "the cat"
    assert response.json()["description"] == "it's magic"

def test_plugin_deactivation(client, mad_hatter_with_mock_plugin):

    response = client.get("/custom-endpoints/endpoint")
    assert response.status_code == 200

    mad_hatter_with_mock_plugin.toggle_plugin("mock_plugin")

    response = client.get("/custom-endpoints/endpoint")
    assert response.status_code == 404