
def test_get_embedder_settings(client):
    
    # act
    response = client.get("/settings/embedder/")
    json = response.json()

    # assert
    assert response.status_code == 200
    assert json["status"] == "success"
    assert "EmbedderFakeConfig" in json["schemas"].keys()
    assert "EmbedderFakeConfig" in json["allowed_configurations"]
    assert json["selected_configuration"] == None # no embedder configured at stratup


def test_upsert_embedder_settings(client):
    
    # prepare embedder config
    invented_key = "some-key"
    embedder_config = {
        "model_name": "text-embedding-ada-002",
        "openai_api_key": invented_key
    }

    # set embedder
    response = client.put("/settings/embedder/EmbedderOpenAIConfig", json=embedder_config)
    json = response.json()

    # verify success
    assert response.status_code == 200
    assert json["status"] == "success"
    assert json["setting"]["value"]["model_name"] == embedder_config["model_name"]


    # retrieve data to check if it was saved in DB
    response = client.get("/settings/embedder/")
    json = response.json()

    # assert
    assert response.status_code == 200
    assert json["selected_configuration"] == 'EmbedderOpenAIConfig'
    assert json["settings"][0]["value"]["openai_api_key"] == invented_key

