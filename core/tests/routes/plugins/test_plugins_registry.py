import os

# TODO: registry responses here should be mocked, at the moment we are actually calling the service

def test_list_registry_plugins(client):

    response = client.get("/plugins")
    json = response.json()

    assert response.status_code == 200
    assert "registry" in json.keys()
    assert type(json["registry"] == list)
    assert len(json["registry"]) > 0

    # registry (see more registry tests in `./test_plugins_registry.py`)
    assert type(json["registry"] == list)
    assert len(json["registry"]) > 0
    
    # query
    for key in ["query"]: # ["query", "author", "tag"]:
        assert key in json["filters"].keys()


def test_list_registry_plugins_by_query(client):

    params = {
        "query": "podcast"
    }
    response = client.get("/plugins", params=params)
    json = response.json()
    print(json)

    assert response.status_code == 200
    assert json["filters"]["query"] == params["query"]
    assert len(json["registry"]) > 0 # found registry plugins with text
    for plugin in json["registry"]:
        plugin_text = plugin["name"] + plugin["description"]
        assert params["query"] in plugin_text # verify searched text


# TOOD: these tests are to be activated when also search by tag and author is activated in core
'''
def test_list_registry_plugins_by_author(client):

    params = {
        "author": "Nicola Corbellini"
    }
    response = client.get("/plugins", params=params)
    json = response.json()

    assert response.status_code == 200
    assert json["filters"]["author"] == params["query"]
    assert len(json["registry"]) > 0 # found registry plugins with author
    for plugin in json["registry"]:
        assert params["author"] in plugin["author_name"] # verify author


def test_list_registry_plugins_by_tag(client):

    params = {
        "tag": "llm"
    }
    response = client.get("/plugins", params=params)
    json = response.json()

    assert response.status_code == 200
    assert json["filters"]["tag"] == params["tag"]
    assert len(json["registry"]) > 0 # found registry plugins with tag
    for plugin in json["registry"]:
        plugin_tags = plugin["tags"].split(", ")
        assert params["tag"] in plugin_tags # verify tag
'''


# take away from the list of availbale registry plugins, the ones that are already installed
def test_list_registry_plugins_without_duplicating_installed_plugins(client):

    # 1. install plugin from registry
    # TODO !!!

    # 2. get available plugins searching for the one just installed
    params = {
        "query": "podcast"
    }
    response = client.get("/plugins", params=params)
    json = response.json()

    # 3. plugin should show up among installed by not among registry ones
    assert response.status_code == 200
    # TODO plugin compares in installed!!!
    # TODO plugin does not appear in registry!!!