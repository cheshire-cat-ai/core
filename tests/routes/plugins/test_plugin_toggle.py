from tests.utils import get_core_plugins_ids, get_mock_plugin_info

def check_active_plugin_properties(plugin):
    assert plugin["id"] == "mock_plugin"
    for k in ["hooks", "tools", "forms", "endpoints"]:
        assert len(plugin[k]) == get_mock_plugin_info()[k]
    
def check_unactive_plugin_properties(plugin):
    assert plugin["id"] == "mock_plugin"
    for k in ["hooks", "tools", "forms", "endpoints"]:
        assert len(plugin[k]) == 0


def test_toggle_non_existent_plugin(client, just_installed_plugin, admin_headers):
    response = client.put("/plugins/toggle/no_plugin", headers=admin_headers)
    response_json = response.json()

    assert response.status_code == 404
    assert response_json["detail"] == "Plugin not found"


def test_deactivate_plugin(client, just_installed_plugin, admin_headers):

    # deactivate
    response = client.put("/plugins/toggle/mock_plugin", headers=admin_headers)

    # GET plugins endpoint lists the plugin
    response = client.get("/plugins", headers=admin_headers)
    installed_plugins = response.json()["installed"]
    assert len(installed_plugins) == len(get_core_plugins_ids()) + 1  # core_plugins and mock_plugin

    mock_plugin = [p for p in installed_plugins if p["id"] == "mock_plugin"][0]
    assert isinstance(mock_plugin["active"], bool)
    assert not mock_plugin["active"]  # plugin NOT active
    check_unactive_plugin_properties(mock_plugin)

    # GET single plugin info, plugin is not active
    response = client.get("/plugins/mock_plugin", headers=admin_headers)
    assert isinstance(response.json()["data"]["active"], bool)
    assert not response.json()["data"]["active"]
    check_unactive_plugin_properties(response.json()["data"])


def test_reactivate_plugin(client, just_installed_plugin, admin_headers):
    # deactivate
    response = client.put("/plugins/toggle/mock_plugin", headers=admin_headers)

    # re-activate
    response = client.put("/plugins/toggle/mock_plugin", headers=admin_headers)

    # GET plugins endpoint lists the plugin
    response = client.get("/plugins", headers=admin_headers)
    installed_plugins = response.json()["installed"]
    assert len(installed_plugins) == len(get_core_plugins_ids()) + 1
    mock_plugin = [p for p in installed_plugins if p["id"] == "mock_plugin"][0]
    assert isinstance(mock_plugin["active"], bool)
    assert mock_plugin["active"]  # plugin active
    check_active_plugin_properties(mock_plugin)

    # GET single plugin info, plugin is active
    response = client.get("/plugins/mock_plugin", headers=admin_headers)
    assert isinstance(response.json()["data"]["active"], bool)
    assert response.json()["data"]["active"]
    check_active_plugin_properties(response.json()["data"])
