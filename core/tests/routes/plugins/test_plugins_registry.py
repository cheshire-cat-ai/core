import os
import shutil
from tests.utils import create_mock_plugin_zip

# TODO: registry responses here should be mocked, at the moment we are actually calling the service


def test_list_registry_plugins(client):
    response = client.get("/plugins")
    json = response.json()

    assert response.status_code == 200
    assert "registry" in json.keys()
    assert isinstance(json["registry"], list)
    assert len(json["registry"]) > 0

    # registry (see more registry tests in `./test_plugins_registry.py`)
    assert isinstance(json["registry"], list)
    assert len(json["registry"]) > 0

    # query
    for key in ["query"]:  # ["query", "author", "tag"]:
        assert key in json["filters"].keys()


def test_list_registry_plugins_by_query(client):
    params = {"query": "podcast"}
    response = client.get("/plugins", params=params)
    json = response.json()

    assert response.status_code == 200
    assert json["filters"]["query"] == params["query"]
    assert len(json["registry"]) > 0  # found registry plugins with text
    for plugin in json["registry"]:
        plugin_text = plugin["name"] + plugin["description"]
        assert params["query"] in plugin_text  # verify searched text

async def mock_registry_download_plugin(url: str):
    return create_mock_plugin_zip(True)

def test_plugin_install_from_registry(client, monkeypatch):
    # Mock the download from the registry creating a zip on-the-fly
    monkeypatch.setattr(
        "cat.routes.plugins.registry_download_plugin", mock_registry_download_plugin
    )

    # during tests, the cat uses a different folder for plugins
    new_plugin_final_folder = "tests/mocks/mock_plugin_folder/mock_plugin"

    if os.path.exists(new_plugin_final_folder):
        shutil.rmtree(new_plugin_final_folder)
    assert not os.path.exists(new_plugin_final_folder)

    # install plugin from registry
    payload = {"url": "https://mockup_url.com"}
    response = client.post("/plugins/upload/registry", json=payload)

    assert response.status_code == 200
    assert response.json()["url"] == payload["url"]
    assert response.json()["info"] == "Plugin is being installed asynchronously"

    # GET plugin endpoint responds
    response = client.get("/plugins/mock_plugin")
    assert response.status_code == 200
    json = response.json()
    assert json["data"]["id"] == "mock_plugin"
    assert isinstance(json["data"]["active"], bool)
    assert json["data"]["active"]

    # GET plugins endpoint lists the plugin
    response = client.get("/plugins")
    assert response.status_code == 200
    installed_plugins = response.json()["installed"]
    installed_plugins_names = list(map(lambda p: p["id"], installed_plugins))
    assert "mock_plugin" in installed_plugins_names
    # both core_plugin and new_plugin are active
    for p in installed_plugins:
        assert isinstance(p["active"], bool)
        assert p["active"]

    # plugin has been actually extracted in (mock) plugins folder
    assert os.path.exists(new_plugin_final_folder)

    # TODO: check for tools and hooks creation


# take away from the list of availbale registry plugins, the ones that are already installed
def test_list_registry_plugins_without_duplicating_installed_plugins(client):
    # 1. install plugin from registry
    # TODO !!!

    # 2. get available plugins searching for the one just installed
    params = {"query": "podcast"}
    response = client.get("/plugins", params=params)
    #json = response.json()

    # 3. plugin should show up among installed by not among registry ones
    assert response.status_code == 200
    # TODO plugin compares in installed!!!
    # TODO plugin does not appear in registry!!!


# TOOD: these tests are to be activated when also search by tag and author is activated in core
"""
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
"""
