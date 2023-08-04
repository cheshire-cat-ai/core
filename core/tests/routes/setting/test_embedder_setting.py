import time

from tests.utils import get_embedded_tools


def test_get_embedder_settings(client):

    # act
    response = client.get("/settings/embedder/")
    json = response.json()

    # assert
    assert response.status_code == 200
    assert json["status"] == "success"
    assert "EmbedderDumbConfig" in json["schemas"].keys()
    assert "EmbedderDumbConfig" in json["allowed_configurations"]
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
    assert json["settings"][0]["value"]["size"] == embedder_config["size"]


def test_upsert_embedder_settings_updates_collections(client):

    tools = get_embedded_tools(client)
    assert len(tools) == 1
    assert len(tools[0]["vector"]) == 2367  # default embedder
    
    # set a different embedder from default one (same class different size)
    embedder_config = {
        "size": 64
    }
    response = client.put("/settings/embedder/EmbedderFakeConfig", json=embedder_config)
    assert response.status_code == 200

    # give some time to re-embed the default tool
    time.sleep(3)

    tools = get_embedded_tools(client)
    assert len(tools) == 1
    assert len(tools[0]["vector"]) == embedder_config["size"]


