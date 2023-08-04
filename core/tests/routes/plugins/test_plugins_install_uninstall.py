import os
import time
import pytest
import shutil
from tests.utils import create_mock_plugin_zip, get_embedded_tools
from fixture_just_installed_plugin import just_installed_plugin


# TODO: these test cases should be splitted in different test functions, with apppropriate setup/teardown
def test_plugin_install_upload_zip(client, just_installed_plugin):

    # during tests, the cat uses a different folder for plugins
    mock_plugin_final_folder = "tests/mocks/mock_plugin_folder/mock_plugin"

    #### PLUGIN IS ALREADY ACTIVE

    # GET plugins endpoint lists the plugin
    response = client.get("/plugins")
    installed_plugins = response.json()["installed"]
    installed_plugins_names = list(map(lambda p: p["id"], installed_plugins))
    assert "mock_plugin" in installed_plugins_names
    # both core_plugin and mock_plugin are active
    for p in installed_plugins:
        assert p["active"] == True

    # plugin has been actually extracted in (mock) plugins folder
    assert os.path.exists(mock_plugin_final_folder)

    # check whether new tools have been embedded
    tools = get_embedded_tools(client)
    tool_names = list(map(lambda t: t["metadata"]["name"], tools))
    assert "random_idea" in tool_names
    

def test_plugin_uninstall(client, just_installed_plugin):

    # during tests, the cat uses a different folder for plugins
    mock_plugin_final_folder = "tests/mocks/mock_plugin_folder/mock_plugin"

    # remove plugin via endpoint (will delete also plugin folder in mock_plugin_folder)
    response = client.delete("/plugins/mock_plugin")
    assert response.status_code == 200
    
    # mock_plugin is not installed in the cat (check both via endpoint and filesystem)
    response = client.get("/plugins")
    installed_plugins_names = list(map(lambda p: p["id"], response.json()["installed"]))
    assert "mock_plugin" not in installed_plugins_names
    assert not os.path.exists(mock_plugin_final_folder) # plugin folder removed from disk

    # plugin tool disappeared
    tools = get_embedded_tools(client)
    tool_names = list(map(lambda t: t["metadata"]["name"], tools))
    assert "random_idea" not in tool_names
