from cat import config


# Probe a *gated* endpoint (/me): /status is intentionally public, so it can't be
# used to exercise auth. With wrong/no credentials this 403s; with the right API
# key it returns the admin user. Uses `anon_client` (no baked-in auth) so we
# control the credential per request.
def http_request(anon_client, headers={}):
    response = anon_client.get("/me", headers=headers)
    return response.status_code, response.json()


def test_http_auth(anon_client):
    wrong_headers = [
        {},  # no header
        {"Authorization": ""},
        {"Authorization": "wrong"},
        {"Authorization": "Bearer wrong"},
    ]

    # all the previous headers result in a 403
    for headers in wrong_headers:
        status_code, json = http_request(anon_client, headers)
        assert status_code == 403
        assert json["detail"] == "Invalid Credentials"

    # allow access if the master API key is right
    status_code, json = http_request(anon_client, {"Authorization": "Bearer meow"})
    assert status_code == 200
    assert json["name"] == "admin"


def test_api_key_on_by_default(anon_client):
    """Out of the box API_KEY="meow", so the master key authenticates."""
    assert config.API_KEY == "meow"
    status_code, _ = http_request(anon_client, {"Authorization": "Bearer meow"})
    assert status_code == 200


def test_api_key_none_keeps_gated_routes_closed(anon_client, monkeypatch):
    """Setting API_KEY=None disables key auth — it does NOT open the gate.

    With no key configured the master key stops authenticating, so gated routes
    stay closed (JWT-only); public routes are unaffected.
    """
    monkeypatch.setitem(config._values, "API_KEY", None)

    # the previously-valid master key no longer authenticates
    status_code, json = http_request(anon_client, {"Authorization": "Bearer meow"})
    assert status_code == 403
    assert json["detail"] == "Invalid Credentials"

    # public route remains reachable
    assert anon_client.get("/status").status_code == 200


def test_all_core_endpoints_secured(anon_client):
    # Intentionally unauthenticated endpoints. Hit without auth/params these may
    # return 200/400/404/422 — the invariant we assert is only that they are NOT
    # auth-gated (no 403). Plugin-provided routes (UI, auth flow) are not active
    # in the core-only suite.
    open_endpoints = [
        "/openapi.json",
        "/docs",
        "/status",  # public: health + auth-handler discovery
    ]

    for endpoint in anon_client.app.routes:
        if not hasattr(endpoint, "methods"):
            continue
        for verb in endpoint.methods:
            response = anon_client.request(verb, endpoint.path)
            if endpoint.path in open_endpoints:
                assert response.status_code != 403
            else:
                assert response.status_code == 403
