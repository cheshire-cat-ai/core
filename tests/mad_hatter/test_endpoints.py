import pytest

from tests.utils import get_mock_plugin_info
from cat.mad_hatter.decorators import Endpoint


def _route(endpoint: Endpoint):
    """The single APIRoute an Endpoint router wraps."""
    return endpoint.routes[0]


def _find(mad_hatter, path, method):
    """Find a plugin Endpoint by its full route path and HTTP method.

    v2 `@endpoint(..., prefix=...)` merges the prefix into the route path, so the
    route's `.path` is the full path (e.g. `/tests/endpoint`).
    """
    for e in mad_hatter.endpoints:
        route = _route(e)
        if route.path == path and method in route.methods:
            return e, route
    raise AssertionError(f"endpoint {method} {path} not found")


def test_endpoints_discovery(mad_hatter_with_mock_plugin):
    mock_plugin_endpoints = mad_hatter_with_mock_plugin.plugins["mock_plugin"].endpoints

    assert len(mock_plugin_endpoints) == get_mock_plugin_info()["endpoints"]

    for e in mock_plugin_endpoints:
        assert isinstance(e, Endpoint)
        assert e.plugin_id == "mock_plugin"
        assert e in mad_hatter_with_mock_plugin.endpoints


def test_endpoint_default_prefix(client, mad_hatter_with_mock_plugin):
    e, route = _find(mad_hatter_with_mock_plugin, "/endpoint", "GET")
    assert route.methods == {"GET"}
    assert route.endpoint() == {"result": "endpoint default prefix"}


def test_endpoint_with_prefix(client, mad_hatter_with_mock_plugin):
    e, route = _find(mad_hatter_with_mock_plugin, "/tests/endpoint", "GET")
    assert route.methods == {"GET"}
    assert route.tags == ["Tests"]


@pytest.mark.parametrize(
    "path,method",
    [
        ("/tests/crud", "GET"),
        ("/tests/crud", "POST"),
        ("/tests/crud/{item_id}", "PUT"),
        ("/tests/crud/{item_id}", "DELETE"),
        ("/tests/role", "GET"),
    ],
)
def test_crud_endpoints_registered(client, mad_hatter_with_mock_plugin, path, method):
    e, route = _find(mad_hatter_with_mock_plugin, path, method)
    assert route.methods == {method}
    assert route.tags == ["Tests"]
    assert e.plugin_id == "mock_plugin"


@pytest.mark.parametrize("switch_type", ["deactivation", "uninstall"])
async def test_endpoints_deactivation_or_uninstall(switch_type, mad_hatter_with_mock_plugin):
    # custom endpoints are registered in mad_hatter
    for e in mad_hatter_with_mock_plugin.plugins["mock_plugin"].endpoints:
        assert isinstance(e, Endpoint)
        assert e.plugin_id == "mock_plugin"
        assert e in mad_hatter_with_mock_plugin.endpoints

    if switch_type == "deactivation":
        await mad_hatter_with_mock_plugin.toggle_plugin("mock_plugin")
        assert mad_hatter_with_mock_plugin.plugins["mock_plugin"].endpoints == []
    else:
        await mad_hatter_with_mock_plugin.uninstall_plugin("mock_plugin")
        assert "mock_plugin" not in mad_hatter_with_mock_plugin.plugins.keys()

    # no more custom endpoints from the mock plugin
    for e in mad_hatter_with_mock_plugin.endpoints:
        assert e.plugin_id != "mock_plugin"
