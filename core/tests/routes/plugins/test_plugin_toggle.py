
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
    assert not mock_plugin[0]["active"] # plugin NOT active
            
    # tool has been taken away
    tools = get_embedded_tools(client)
    tool_names = list(map(lambda t: t["metadata"]["name"], tools))
    assert not "random_idea" in tool_names
    

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
    assert mock_plugin[0]["active"] # plugin active
            
    # tool has been re-embedded
    tools = get_embedded_tools(client)
    tool_names = list(map(lambda t: t["metadata"]["name"], tools))
    assert "random_idea" in tool_names