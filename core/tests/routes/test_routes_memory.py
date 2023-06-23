def test_get_collections(client):
    # prepare test data
    embedder_config = {"size": 128}
    response = client.put("/settings/embedder/EmbedderFakeConfig",
                          json=embedder_config)

    # Act
    response = client.get(
        "/memory/collections")

    # Assert
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # here should be 0 because we didn't add any memory yet
    assert response.json()["collections"][0]["vectors_count"] == 0
