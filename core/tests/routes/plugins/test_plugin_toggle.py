
from tests.utils import get_embedded_tools
from fixture_just_installed_plugin import just_installed_plugin


def test_toggle_non_existent_plugin(client, just_installed_plugin):
    
    response = client.put("/plugins/toggle/no_plugin")
    response_json = response.json()

    assert response.status_code == 404
    assert response_json["detail"]["error"] == "Plugin not found"


def test_activate_plugin(client, just_installed_plugin):

    # GET plugins endpoint lists the plugin
    response = client.get("/plugins")
    installed_plugins_names = list(map(lambda p: p["id"], response.json()["installed"]))
    print(installed_plugins_names)
    assert "mock_plugin" in installed_plugins_names
    
    # check whether new tools have been embedded
    tools = get_embedded_tools(client)
    tool_names = list(map(lambda t: t["metadata"]["name"], tools))
    assert "random_idea" not in tool_names
    

def test_deactivate_plugin(client, just_installed_plugin):
    
    # TODO
    pass
