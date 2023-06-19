def test_upsert_embedder_settings_success(client):
    
    # prepare test data
    embedder_config = {"size": 128}

    # act
    response = client.put("/settings/embedder/EmbedderFakeConfig",
                          json=embedder_config)

    # assert
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["setting"]["value"]["size"] == embedder_config["size"]


def test_get_embedder_settings(client):
    
    # act
    response = client.get("/settings/embedder/")
    json = response.json()

    # assert
    assert response.status_code == 200
    assert json["status"] == "success"
    assert "EmbedderFakeConfig" in json["schemas"].keys()
    assert "EmbedderFakeConfig" in json["allowed_configurations"]
    assert json["selected_configuration"] == "EmbedderFakeConfig"