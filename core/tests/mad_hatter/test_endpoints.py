import pytest
from cat.mad_hatter.decorators import CustomEndpoint

def test_endpoints_discovery(mad_hatter_with_mock_plugin):

    # discovered endpoints are cached
    mock_plugin_endpoints = mad_hatter_with_mock_plugin.plugins["mock_plugin"].endpoints
    assert mock_plugin_endpoints == mad_hatter_with_mock_plugin.endpoints

    # discovered endpoints
    assert len(mock_plugin_endpoints) == 6

    # basic properties
    for h in mock_plugin_endpoints:
        assert isinstance(h, CustomEndpoint)
        assert h.plugin_id == "mock_plugin"


def test_endpoint_decorator(client, mad_hatter_with_mock_plugin):
    # Find specific endpoint by path/prefix/method
    endpoints = mad_hatter_with_mock_plugin.endpoints
    endpoint = next(e for e in endpoints 
                   if e.path == "/endpoint" 
                   and e.prefix == "/custom" 
                   and "GET" in e.methods)
    
    assert endpoint.name == "/custom/endpoint"
    assert endpoint.prefix == "/custom"
    assert endpoint.path == "/endpoint"
    assert endpoint.methods == {"GET"}
    assert endpoint.tags == ["Custom Endpoints"]
    assert endpoint.function() == {"result":"endpoint default prefix"}

def test_endpoint_decorator_prefix(client, mad_hatter_with_mock_plugin):
    endpoints = mad_hatter_with_mock_plugin.endpoints
    endpoint = next(e for e in endpoints 
                   if e.path == "/endpoint" 
                   and e.prefix == "/tests" 
                   and "GET" in e.methods)
    
    assert endpoint.name == "/tests/endpoint"
    assert endpoint.prefix == "/tests"
    assert endpoint.path == "/endpoint"
    assert endpoint.methods == {"GET"}
    assert endpoint.tags == ["Tests"]

def test_get_endpoint(client, mad_hatter_with_mock_plugin):
    endpoints = mad_hatter_with_mock_plugin.endpoints
    endpoint = next(e for e in endpoints 
                   if e.path == "/crud" 
                   and e.prefix == "/tests" 
                   and "GET" in e.methods)
    
    assert endpoint.name == "/tests/crud"
    assert endpoint.prefix == "/tests"
    assert endpoint.path == "/crud"
    assert endpoint.methods == {"GET"}
    assert endpoint.tags == ["Tests"]

def test_post_endpoint(client, mad_hatter_with_mock_plugin):
    endpoints = mad_hatter_with_mock_plugin.endpoints
    endpoint = next(e for e in endpoints 
                   if e.path == "/crud" 
                   and e.prefix == "/tests" 
                   and "POST" in e.methods)
    
    assert endpoint.name == "/tests/crud"
    assert endpoint.prefix == "/tests"  
    assert endpoint.path == "/crud"
    assert endpoint.methods == {"POST"}
    assert endpoint.tags == ["Tests"]


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