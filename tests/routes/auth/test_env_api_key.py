import pytest


# utility to make http requests with some headers
def http_request(client, headers={}):
    response = client.get("/status", headers=headers)
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

    # allow access if CCAT_API_KEY is right
    headers = {"Authorization": "Bearer meow"}
    status_code, json = http_request(client, headers)
    assert status_code == 200
    assert json["status"] == "We're all mad here, dear!"


def test_all_core_endpoints_secured(client):
    # using client fixture, so both http and ws keys are set

    open_endpoints = [
        "/openapi.json",
        "/docs",
        "/auth/handlers",
        "/auth/login/{name}",
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
                    assert response.status_code in {200, 400}
                else:
                    assert response.status_code == 403
