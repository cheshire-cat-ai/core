import pytest

from cat.mad_hatter.mad_hatter import MadHatter
from cat.mad_hatter.decorators import CustomEndpoint

from tests.utils import create_mock_plugin_zip

# this function will be run before each test function
@pytest.fixture
def mad_hatter(client):  # client here injects the monkeypatched version of the cat

    # each test is given the mad_hatter instance (it's a singleton)
    mad_hatter = MadHatter()

    # install plugin
    new_plugin_zip_path = create_mock_plugin_zip(flat=True)
    mad_hatter.install_plugin(new_plugin_zip_path)

    yield mad_hatter


def test_endpoints_discovery(mad_hatter):
    mock_plugin_endpoints = mad_hatter.plugins["mock_plugin"].endpoints

    assert len(mock_plugin_endpoints) == 4

    for h in mock_plugin_endpoints:
        assert isinstance(h, CustomEndpoint)
        assert h.plugin_id == "mock_plugin"


def test_endpoint_decorator(client):

    response = client.get("/custom_endpoints/endpoint")

    assert response.status_code == 200
    
    assert response.json()["result"] == "endpoint default prefix"


def test_endpoint_decorator_prefix(client):

    response = client.get("/tests/endpoint")

    assert response.status_code == 200
    
    assert response.json()["result"] == "endpoint prefix tests"


def test_get_endpoint(client):

    response = client.get("/tests/get")

    assert response.status_code == 200
    
    assert response.json()["result"] == "ok"
    assert response.json()["stray_user_id"] == "user"


def test_post_endpoint(client):

    payload = {"name": "the cat", "description" : "it's magic"}
    response = client.post("/tests/post", json=payload)

    assert response.status_code == 200

    assert response.json()["name"] == "the cat"
    assert response.json()["description"] == "it's magic"