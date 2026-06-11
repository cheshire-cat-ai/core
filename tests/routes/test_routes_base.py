

def test_ping_success(client, admin_headers, api_prefix):
    response = client.get(f"{api_prefix}/status", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "We're all mad here, dear!"


def test_agents_list(client, admin_headers, api_prefix):
    """GET /agents returns the list of registered agents."""
    response = client.get(f"{api_prefix}/agents", headers=admin_headers)
    assert response.status_code == 200
    agents = response.json()
    assert isinstance(agents, list)
    # default agent should be registered
    assert any(a["slug"] == "default" for a in agents)
