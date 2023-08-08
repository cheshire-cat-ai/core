import time

from tests.utils import get_embedded_tools


def test_get_all_embedder_settings(client):

    response = client.get("/embedder/settings")
    json = response.json()

    assert response.status_code == 200
    assert json["status"] == "success"
    assert "EmbedderDumbConfig" in json["schemas"].keys()
    assert "EmbedderDumbConfig" in json["allowed_configurations"]
    assert json["selected_configuration"] == None # no embedder configured at stratup


def test_get_embedder_settings_non_existent(client):

    non_existent_embedder_name = "EmbedderNonExistentConfig"
    response = client.get(f"/embedder/settings/{non_existent_embedder_name}")
    json = response.json()

    assert response.status_code == 400
    assert f"{non_existent_embedder_name} not supported" in json["detail"]["error"]


def test_get_embedder_settings(client):

    embedder_name = "EmbedderDumbConfig"
    response = client.get(f"/embedder/settings/{embedder_name}")
    json = response.json()

    assert response.status_code == 200
    assert json["status"] == "success"
    assert json["settings"] == {}  # Dumb Embedder has indeed an empty config (no options)
    assert json["schema"]["languageEmbedderName"] == embedder_name
    assert json["schema"]["type"] == "object"


def test_upsert_embedder_settings(client):
    
    # set a different embedder from default one (same class different size # TODO: have another fake/test embedder class)
    embedder_config = {
        "size": 64
    }
    response = client.put("/embedder/settings/EmbedderFakeConfig", json=embedder_config)
    json = response.json()

    # verify success
    assert response.status_code == 200
    assert json["status"] == "success"
    assert json["setting"]["value"]["size"] == embedder_config["size"]

    # retrieve embedders settings to check if it was saved in DB
    response = client.get("/embedder/settings/")
    json = response.json()
    assert response.status_code == 200
    assert json["selected_configuration"] == 'EmbedderFakeConfig'
    assert json["settings"][0]["value"]["size"] == embedder_config["size"]

    # check also specific embedder endpoint
    response = client.get("/embedder/settings/EmbedderFakeConfig")
    json = response.json()
    assert response.status_code == 200
    assert json["settings"]["size"] == embedder_config["size"]


def test_upsert_embedder_settings_updates_collections(client):

    tools = get_embedded_tools(client)
    assert len(tools) == 1
    assert len(tools[0]["vector"]) == 2367  # default embedder
    
    # set a different embedder from default one (same class different size)
    embedder_config = {
        "size": 64
    }
    response = client.put("/embedder/settings/EmbedderFakeConfig", json=embedder_config)
    assert response.status_code == 200

    tools = get_embedded_tools(client)
    assert len(tools) == 1
    assert len(tools[0]["vector"]) == embedder_config["size"]


