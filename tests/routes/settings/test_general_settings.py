"""Tests for the unified /settings endpoint (core suite, core-only).

CoreSettings has `service_type = "config"` and `slug = "core"`, registered under
`plugin_id = "core"`, so its composite id is `core__config__core`.
"""

CORE_ID = "core__config__core"


def test_get_settings_list(client, admin_headers):
    """GET /settings returns a list of services that have settings."""
    response = client.get("/settings", headers=admin_headers)
    assert response.status_code == 200

    entries = response.json()
    assert isinstance(entries, list)

    core_entry = next((e for e in entries if e["id"] == CORE_ID), None)
    assert core_entry is not None
    assert core_entry["type"] == "config"
    assert core_entry["slug"] == "core"
    assert core_entry["name"] == "Core Settings"
    assert core_entry["plugin_id"] == "core"
    assert core_entry["schema"] is not None
    assert isinstance(core_entry["value"], dict)


def test_put_settings_success(client, admin_headers):
    """PUT /settings/{id} updates core settings."""
    payload = {"default_llm": "default:default", "default_embedder": "default:default"}
    response = client.put(f"/settings/{CORE_ID}", json=payload, headers=admin_headers)
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["id"] == CORE_ID
    assert data["slug"] == "core"
    assert data["type"] == "config"
    assert data["value"]["default_llm"] == "default:default"
    assert data["schema"] is not None


def test_put_settings_persists(client, admin_headers):
    """PUT then GET shows persisted settings."""
    payload = {"default_llm": "default:default", "default_embedder": "default:default"}
    client.put(f"/settings/{CORE_ID}", json=payload, headers=admin_headers)

    response = client.get("/settings", headers=admin_headers)
    assert response.status_code == 200

    core_entry = next((e for e in response.json() if e["id"] == CORE_ID), None)
    assert core_entry is not None
    assert core_entry["value"]["default_llm"] == "default:default"


def test_put_settings_unknown_service(client, admin_headers):
    """PUT /settings/{id} with unknown id returns 404."""
    response = client.put(
        "/settings/nonexistent__model_providers__fake",
        json={"key": "value"},
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_put_settings_invalid_id_format(client, admin_headers):
    """PUT /settings/{id} with malformed id returns 404."""
    response = client.put(
        "/settings/invalid_id",
        json={"key": "value"},
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_settings_requires_admin(client):
    """GET /settings is admin-gated."""
    response = client.get("/settings")
    assert response.status_code == 403
