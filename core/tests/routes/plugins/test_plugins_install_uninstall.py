import os
import time
import shutil
from tests.utils import get_procedural_memory_contents
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
    procedures = get_procedural_memory_contents(client)
    assert len(procedures) == 9 # two tools, 4 tools examples, 3  form triggers
    procedures_names = list(map(lambda t: t["metadata"]["source"], procedures))
    assert procedures_names.count("mock_tool") == 3
    assert procedures_names.count("get_the_time") == 3
    assert procedures_names.count("PizzaForm") == 3

    procedures_sources = list(map(lambda t: t["metadata"]["type"], procedures))
    assert procedures_sources.count("tool") == 6
    assert procedures_sources.count("form") == 3

    procedures_triggers = list(map(lambda t: t["metadata"]["trigger_type"], procedures))
    assert procedures_triggers.count("start_example") == 6
    assert procedures_triggers.count("description") == 3


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
    procedures = get_procedural_memory_contents(client)
    assert len(procedures) == 3
    procedures_names = set(map(lambda t: t["metadata"]["source"], procedures))
    assert procedures_names == {"get_the_time"}

    # only examples for core tool
    # Ensure unique procedure sources
    procedures_sources = list(map(lambda t: t["metadata"]["type"], procedures)) 
    assert procedures_sources.count("tool") == 3
    assert procedures_sources.count("form") == 0

    tool_start_examples = []
    form_start_examples = []
    for p in procedures:
        if p["metadata"]["type"] == "tool" and p["metadata"]["trigger_type"] == "start_example":
            tool_start_examples.append(p)

        if p["metadata"]["type"] == "form" and p["metadata"]["trigger_type"] == "start_example":
            form_start_examples.append(p)
    
    assert len(tool_start_examples) == 2
    assert len(form_start_examples) == 0
