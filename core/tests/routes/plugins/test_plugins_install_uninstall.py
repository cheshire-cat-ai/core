import os
import time
import shutil
from tests.utils import get_embedded_tools
from fixture_just_installed_plugin import just_installed_plugin


# NOTE: here we test zip upload install
# install from registry is in `./test_plugins_registry.py`
def test_plugin_install_from_zip(client, just_installed_plugin):

    # during tests, the cat uses a different folder for plugins
    mock_plugin_final_folder = "tests/mocks/mock_plugin_folder/mock_plugin"

    #### PLUGIN IS ALREADY ACTIVE

    # GET plugin endpoint responds
    response = client.get(f"/plugins/mock_plugin")
    assert response.status_code == 200
    json = response.json()
    assert json["data"]["id"] == "mock_plugin"
    assert json["data"]["active"] == True

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

    # check whether new tool has been embedded
    tools = get_embedded_tools(client)
    assert len(tools) == 2
    tool_names = list(map(lambda t: t["metadata"]["name"], tools))
    assert "mock_tool" in tool_names
    assert "get_the_time" in tool_names # from core_plugin


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
    assert len(tools) == 1
    tool_names = list(map(lambda t: t["metadata"]["name"], tools))
    assert "mock_tool" not in tool_names
    assert "get_the_time" in tool_names # from core_plugin



