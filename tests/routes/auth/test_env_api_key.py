import pytest


# utility to make http requests with some headers.
# Probes a *gated* endpoint (/me): /status is intentionally public, so it can't
# be used to exercise auth. With wrong/no credentials this 403s; with the right
# API key it returns the admin user.
def http_request(client, headers={}):
    response = client.get("/me", headers=headers)
    return response.status_code, response.json()


def test_http_auth(client):

    wrong_headers = [
        {}, # no header
        { "Authorization": "" },
        { "Authorization": "wrong" },
        { "Authorization": "Bearer wrong" }
    ]

    # all the previous headers result in a 403
    for headers in wrong_headers:
        status_code, json = http_request(client, headers)
        assert status_code == 403
        assert json["detail"] == "Invalid Credentials"

    # allow access if API_KEY is right
    headers = {"Authorization": "Bearer meow"}
    status_code, json = http_request(client, headers)
    assert status_code == 200
    assert json["name"] == "admin"


def test_all_core_endpoints_secured(client):
    # using client fixture, so both http and ws keys are set

    # Intentionally unauthenticated endpoints. Anyone can reach them before
    # logging in: API docs, the public status (the SPA reads its auth_handlers
    # to build "login with ..." buttons), the login flow (a plugin), and the
    # frontend itself. Hit without auth/params these may return 200/400/404/422
    # — the invariant we assert is only that they are NOT auth-gated (no 403).
    open_endpoints = [
        "/",                          # frontend index (UI plugin)
        "/openapi.json",
        "/docs",
        "/status",                    # public: health + auth-handler discovery
        "/assets/{path:path}",        # frontend static assets (UI plugin)
        "/auth/handlers",
        "/auth/login/{name}",         # login flow (simple_oauth plugin)
        "/auth/callback/{name}",
        "/auth/logout",
        "/auth/internal-idp",
        "/auth/internal-idp/login",
    ]

    # test all endpoints are secured
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

                if endpoint.path in open_endpoints:
                    # reachable without authentication (not auth-gated)
                    assert response.status_code != 403
                else:
                    assert response.status_code == 403
