def _get_installed(client):
    response = client.get("/plugins")
    assert response.status_code == 200
    return response.json()


def test_toggle_non_existent_plugin(client, just_installed_plugin):
    response = client.put("/plugins/no_plugin/toggle")
    assert response.status_code == 404
    assert response.json()["detail"] == "Plugin not found"


def test_deactivate_plugin(client, just_installed_plugin):
    # deactivate
    response = client.put("/plugins/mock_plugin/toggle")
    assert response.status_code == 200

    # GET plugins lists the (now inactive) plugin — core-only, so it's the only one
    installed = _get_installed(client)
    mock_plugin = next(p for p in installed if p["id"] == "mock_plugin")
    assert isinstance(mock_plugin["active"], bool)
    assert not mock_plugin["active"]

    # GET single plugin info reflects inactive state
    response = client.get("/plugins/mock_plugin")
    assert response.status_code == 200
    assert response.json()["active"] is False


def test_reactivate_plugin(client, just_installed_plugin):
    # deactivate then re-activate
    client.put("/plugins/mock_plugin/toggle")
    response = client.put("/plugins/mock_plugin/toggle")
    assert response.status_code == 200

    installed = _get_installed(client)
    mock_plugin = next(p for p in installed if p["id"] == "mock_plugin")
    assert mock_plugin["active"]

    response = client.get("/plugins/mock_plugin")
    assert response.status_code == 200
    assert response.json()["active"] is True
