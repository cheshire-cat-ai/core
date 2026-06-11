from cat.urls import API_PREFIX

# utility to make http requests with some headers
def http_request(client, path, headers={}):
    response = client.get(path, headers=headers)
    return response.status_code, response.json()


def test_status_is_public(client, api_prefix):
    """Status endpoint is intentionally public (health check for load balancers, k8s probes)."""
    response = client.get(f"{api_prefix}/status")
    assert response.status_code == 200
    json = response.json()
    assert json["status"] == "We're all mad here, dear!"
    assert "version" in json


def test_http_auth(client, api_prefix):
    """Verify authentication enforcement on protected endpoints."""
    wrong_headers = [
        {}, # no header
        { "Authorization": "" },
        { "Authorization": "wrong" },
        { "Authorization": "Bearer wrong" }
    ]

    # unauthenticated access is denied on protected endpoints
    for headers in wrong_headers:
        status_code, json = http_request(client, f"{api_prefix}/plugins", headers)
        assert status_code == 403
        assert json["detail"] == "Invalid Credentials"

    # authenticated access works
    headers = {"Authorization": "Bearer meow"}
    status_code, json = http_request(client, f"{api_prefix}/plugins", headers)
    assert status_code == 200


# endpoints that are intentionally open (no auth required)
OPEN_ENDPOINTS = {
    "/openapi.json",
    "/docs",
    "/",
    # status is a public health check
    f"{API_PREFIX}/status",
    # auth flow must be public (login, logout, callback, idp)
    f"{API_PREFIX}/auth/logout",
    f"{API_PREFIX}/auth/login/{{name}}",
    f"{API_PREFIX}/auth/callback/{{name}}",
    "/auth/internal-idp",
    "/auth/internal-idp/login",
    # static assets from plugins (e.g. UI)
    "/assets/{path:path}",
}


def test_all_core_endpoints_secured(client):
    """Every endpoint not in OPEN_ENDPOINTS must return 403 without auth."""

    for endpoint in client.app.routes:

        # static admin files (redirect to login)
        if "/admin" in endpoint.path:
            response = client.get(endpoint.path, follow_redirects=False)
            assert response.status_code == 307
        # static files http endpoints (open)
        elif "/core-static" in endpoint.path:
            response = client.get(endpoint.path)
            assert response.status_code in {200, 404}
        # REST API http endpoints
        elif hasattr(endpoint, "methods"):
            for verb in endpoint.methods:
                response = client.request(verb, endpoint.path)

                if endpoint.path in OPEN_ENDPOINTS:
                    assert response.status_code in {200, 400, 404, 422}
                else:
                    assert response.status_code == 403
