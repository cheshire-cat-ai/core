
from tests.utils import get_embedded_tools
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
    tools = get_embedded_tools(client)
    assert len(tools) == 1
    tool_names = list(map(lambda t: t["metadata"]["name"], tools))
    assert "mock_tool" not in tool_names
    assert "get_the_time" in tool_names # from core_plugin
    

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

    # tool has been re-embedded
    tools = get_embedded_tools(client)
    assert len(tools) == 2
    tool_names = list(map(lambda t: t["metadata"]["name"], tools))
    assert "mock_tool" in tool_names
    assert "get_the_time" in tool_names # from core_plugin