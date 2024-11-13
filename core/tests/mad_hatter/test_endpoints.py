import pytest
from cat.mad_hatter.decorators import CustomEndpoint
from tests.mocks.mock_plugin.mock_endpoint import Item

def test_endpoints_discovery(mad_hatter_with_mock_plugin):

    # discovered endpoints are cached
    mock_plugin_endpoints = mad_hatter_with_mock_plugin.plugins["mock_plugin"].endpoints
    assert mock_plugin_endpoints == mad_hatter_with_mock_plugin.endpoints
    
    # discovered endpoints
    assert len(mock_plugin_endpoints) == 4

    # basic properties
    for h in mock_plugin_endpoints:
        assert isinstance(h, CustomEndpoint)
        assert h.plugin_id == "mock_plugin"


def test_endpoint_decorator(client, mad_hatter_with_mock_plugin):
        
    endpoint = mad_hatter_with_mock_plugin.endpoints[0]
    
    assert endpoint.name == "/custom/endpoint"
    assert endpoint.prefix == "/custom"
    assert endpoint.path == "/endpoint"
    assert endpoint.methods == ["GET"]
    assert endpoint.tags == ["Custom Endpoints"]
    assert endpoint.function() == {"result":"endpoint default prefix"}


def test_endpoint_decorator_prefix(client, mad_hatter_with_mock_plugin):

    endpoint = mad_hatter_with_mock_plugin.endpoints[1]
    
    assert endpoint.name == "/tests/endpoint"
    assert endpoint.prefix == "/tests"
    assert endpoint.path == "/endpoint"
    assert endpoint.methods == ["GET"]
    assert endpoint.tags == ["Tests"]
    assert endpoint.function() == {"result":"endpoint prefix tests"}


def test_get_endpoint(client, mad_hatter_with_mock_plugin):

    endpoint = mad_hatter_with_mock_plugin.endpoints[2]
    
    assert endpoint.name == "/tests/get"
    assert endpoint.prefix == "/tests"
    assert endpoint.path == "/get"
    assert endpoint.methods == ["GET"]
    assert endpoint.tags == ["Tests"]
    # too complicated to simulate the request arguments here,
    #  see tests/routes/test_custom_endpoints.py

def test_post_endpoint(client, mad_hatter_with_mock_plugin):

    endpoint = mad_hatter_with_mock_plugin.endpoints[3]
    
    assert endpoint.name == "/tests/post"
    assert endpoint.prefix == "/tests"
    assert endpoint.path == "/post"
    assert endpoint.methods == ["POST"]
    assert endpoint.tags == ["Tests"]

    payload = Item(name="the cat", description="it's magic")
    assert endpoint.function(payload) == payload.model_dump()


@pytest.mark.parametrize("switch_type", ["deactivation", "uninstall"])
def test_endpoints_deactivation_or_uninstall(switch_type, mad_hatter_with_mock_plugin): 

    # custom endpoints are registered in mad_hatter
    for h in mad_hatter_with_mock_plugin.endpoints:
        assert isinstance(h, CustomEndpoint)
        assert h.plugin_id == "mock_plugin"

    if switch_type == "deactivation":
        # deactivate plugin
        mad_hatter_with_mock_plugin.toggle_plugin("mock_plugin")
    else:
        # uninstall plugin
        mad_hatter_with_mock_plugin.uninstall_plugin("mock_plugin")

    # no more custom endpoints
    assert mad_hatter_with_mock_plugin.endpoints == []