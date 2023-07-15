def test_ping_success(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "We're all mad here, dear!"
