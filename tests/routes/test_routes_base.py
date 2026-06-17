
from tests.utils import send_http_message

def test_ping_success(client, admin_headers):
    response = client.get("/status", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "We're all mad here, dear!"


def test_http_message(client, admin_headers):

    response = send_http_message("hello!", client, headers=admin_headers)
    assert "You did not configure" in response["text"]