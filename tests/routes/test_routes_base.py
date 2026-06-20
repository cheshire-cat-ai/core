from tests.utils import send_http_message


def test_status_success(client):
    response = client.get("/status")
    assert response.status_code == 200
    assert response.json()["status"] == "We're all mad here, dear!"


def test_status_is_public(client):
    # /status is intentionally public (the SPA reads auth_handlers from it)
    response = client.get("/status")
    assert response.status_code == 200


def test_http_message_default_agent(client):
    # core-only: the default model provider is the "not configured" placeholder,
    # which answers with a clear next step instead of crashing.
    response = send_http_message("hello!", client)
    assert "configured" in response["text"].lower()
