
def test_toggle_non_existent_plugin(client):
    
    response = client.put("/plugins/toggle/no_plugin")
    response_json = response.json()

    assert response.status_code == 404
    assert response_json["detail"]["error"] == "Plugin not found"


def test_toggle_active_plugin(client):
    
    # TODO
    pass


def test_toggle_inactive_plugin(client):
    
    # TODO
    pass
