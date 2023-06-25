def test_call(client):
    response = client.get("/static/")
    assert response.status_code == 404
