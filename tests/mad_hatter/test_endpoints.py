import pytest
from tests.utils import get_mock_plugin_info
from cat.mad_hatter.decorators import Endpoint


def test_endpoints_discovery(mad_hatter_with_mock_plugin):

    # discovered endpoints are cached
    mock_plugin_endpoints = mad_hatter_with_mock_plugin.plugins["mock_plugin"].endpoints
    
    # discovered endpoints
    assert len(mock_plugin_endpoints) == get_mock_plugin_info()["endpoints"]

    # basic properties
    for h in mock_plugin_endpoints:
        assert isinstance(h, Endpoint)
        assert h.plugin_id == "mock_plugin"
        assert h in mad_hatter_with_mock_plugin.endpoints


def test_endpoint_decorator(client, mad_hatter_with_mock_plugin):

    for e in mad_hatter_with_mock_plugin.endpoints:
        if e.name == "/custom/endpoint":
            endpoint = e
            break
    
    assert endpoint.prefix == "/custom"
    assert endpoint.path == "/endpoint"
    assert endpoint.methods == {"GET"}
    assert endpoint.tags == ["Custom Endpoints"]
    assert endpoint.function() == {"result":"endpoint default prefix"}


def test_endpoint_decorator_prefix(client, mad_hatter_with_mock_plugin):
    
    for e in mad_hatter_with_mock_plugin.endpoints:
        if e.name == "/tests/endpoint":
            endpoint = e
            break
    
    assert endpoint.prefix == "/tests"
    assert endpoint.path == "/endpoint"
    assert endpoint.methods == {"GET"}
    assert endpoint.tags == ["Tests"]


def test_get_endpoint(client, mad_hatter_with_mock_plugin):
    
    for e in mad_hatter_with_mock_plugin.endpoints:
        if e.path == "/crud" and "GET" in e.methods:
            endpoint = e
            break
    
    assert endpoint.name == "/tests/crud"
    assert endpoint.prefix == "/tests"
    assert endpoint.methods == {"GET"}
    assert endpoint.tags == ["Tests"]


def test_post_endpoint(client, mad_hatter_with_mock_plugin):

    for e in mad_hatter_with_mock_plugin.endpoints:
        if e.path == "/crud" and "POST" in e.methods:
            endpoint = e
            break
    
    assert endpoint.name == "/tests/crud"
    assert endpoint.prefix == "/tests"  
    assert endpoint.methods == {"POST"}
    assert endpoint.tags == ["Tests"]


def test_put_endpoint(client, mad_hatter_with_mock_plugin):

    for e in mad_hatter_with_mock_plugin.endpoints:
        if e.path == "/crud/{item_id}" and "PUT" in e.methods:
            endpoint = e
            break
    
    assert endpoint.name == "/tests/crud/{item_id}"
    assert endpoint.prefix == "/tests"  
    assert endpoint.methods == {"PUT"}
    assert endpoint.tags == ["Tests"]


def test_delete_endpoint(client, mad_hatter_with_mock_plugin):

    for e in mad_hatter_with_mock_plugin.endpoints:
        if e.path == "/crud/{item_id}" and "DELETE" in e.methods:
            endpoint = e
            break
    
    assert endpoint.name == "/tests/crud/{item_id}"
    assert endpoint.prefix == "/tests"  
    assert endpoint.methods == {"DELETE"}
    assert endpoint.tags == ["Tests"]


def test_custom_role_endpoint(client, mad_hatter_with_mock_plugin):

    for e in mad_hatter_with_mock_plugin.endpoints:
        if e.path == "/role" and "GET" in e.methods:
            endpoint = e
            break

    assert endpoint.name == "/tests/role"
    assert endpoint.prefix == "/tests"  
    assert endpoint.methods == {"GET"}
    assert endpoint.tags == ["Tests"]


@pytest.mark.parametrize("switch_type", ["deactivation", "uninstall"])
def test_endpoints_deactivation_or_uninstall(switch_type, mad_hatter_with_mock_plugin): 

    # custom endpoints are registered in mad_hatter
    for h in mad_hatter_with_mock_plugin.plugins["mock_plugin"].endpoints:
        assert isinstance(h, Endpoint)
        assert h.plugin_id == "mock_plugin"
        assert h in mad_hatter_with_mock_plugin.endpoints

    if switch_type == "deactivation":
        # deactivate plugin
        mad_hatter_with_mock_plugin.toggle_plugin("mock_plugin")
        assert mad_hatter_with_mock_plugin.plugins["mock_plugin"].endpoints == []
    else:
        # uninstall plugin
        mad_hatter_with_mock_plugin.uninstall_plugin("mock_plugin")
        assert "mock_plugin" not in mad_hatter_with_mock_plugin.plugins.keys()

    # no more custom endpoints
    for e in mad_hatter_with_mock_plugin.endpoints:
        assert e.plugin_id != "mock_plugin"