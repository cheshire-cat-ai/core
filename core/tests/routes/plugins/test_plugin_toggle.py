
from tests.utils import get_procedural_memory_contents
from fixture_just_installed_plugin import just_installed_plugin


def test_toggle_non_existent_plugin(client, just_installed_plugin):
    
    response = client.put("/plugins/toggle/no_plugin")
    response_json = response.json()

    assert response.status_code == 404
    assert response_json["detail"]["error"] == "Plugin not found"


def test_deactivate_plugin(client, just_installed_plugin):

    # deactivate
    response = client.put("/plugins/toggle/mock_plugin")
    
    # GET plugins endpoint lists the plugin
    response = client.get("/plugins")
    installed_plugins = response.json()["installed"]
    mock_plugin = [p for p in installed_plugins if p["id"] == "mock_plugin"]
    assert len(mock_plugin) == 1 # plugin installed
    assert mock_plugin[0]["active"] == False # plugin NOT active

    # GET single plugin info, plugin is not active
    response = client.get("/plugins/mock_plugin")
    assert response.json()["data"]["active"] == False
            
    # tool has been taken away
    procedures = get_procedural_memory_contents(client)
    assert len(procedures) == 3
    procedures_sources = list(map(lambda t: t["metadata"]["source"], procedures))
    assert "mock_tool" not in procedures_sources
    assert "PizzaForm" not in procedures_sources
    assert "get_the_time" in procedures_sources # from core_plugin

    # only examples for core tool
    procedures_types = list(map(lambda t: t["metadata"]["type"], procedures))
    assert procedures_types.count("tool") == 3
    assert procedures_types.count("form") == 0
    procedures_triggers = list(map(lambda t: t["metadata"]["trigger_type"], procedures))
    assert procedures_triggers.count("start_example") == 2
    assert procedures_triggers.count("description") == 1
    

def test_reactivate_plugin(client, just_installed_plugin):
    
    # deactivate
    response = client.put("/plugins/toggle/mock_plugin")

    # re-activate
    response = client.put("/plugins/toggle/mock_plugin")

    # GET plugins endpoint lists the plugin
    response = client.get("/plugins")
    installed_plugins = response.json()["installed"]
    mock_plugin = [p for p in installed_plugins if p["id"] == "mock_plugin"]
    assert len(mock_plugin) == 1 # plugin installed
    assert mock_plugin[0]["active"] == True # plugin active

    # GET single plugin info, plugin is active
    response = client.get("/plugins/mock_plugin")
    assert response.json()["data"]["active"] == True

    # check whether procedures have been re-embedded
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
