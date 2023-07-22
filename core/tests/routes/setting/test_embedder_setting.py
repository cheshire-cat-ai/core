
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
    
    # set a different embedder from default one (same class different size # TODO: have another fake/test embedder class)
    embedder_config = {
        "size": 64
    }
    response = client.put("/settings/embedder/EmbedderFakeConfig", json=embedder_config)
    json = response.json()

    # verify success
    assert response.status_code == 200
    assert json["status"] == "success"
    assert json["setting"]["value"]["size"] == embedder_config["size"]


    # retrieve data to check if it was saved in DB
    response = client.get("/settings/embedder/")
    json = response.json()

    # assert
    assert response.status_code == 200
    assert json["selected_configuration"] == 'EmbedderFakeConfig'
    assert json["settings"][0]["value"]["size"] == 64
