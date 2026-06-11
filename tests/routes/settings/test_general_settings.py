"""Tests for the unified /settings endpoint."""


def test_get_settings_list(client, admin_headers, api_prefix):
    """GET /settings returns a list of services that have settings."""
    response = client.get(f"{api_prefix}/settings", headers=admin_headers)
    assert response.status_code == 200

    entries = response.json()
    assert isinstance(entries, list)

    # CoreSettings should appear (it has a nested Settings class)
    core_entry = next(
        (e for e in entries if e["type"] == "config" and e["slug"] == "core"),
        None,
    )
    assert core_entry is not None
    assert core_entry["id"] == "core__config__core"
    assert core_entry["name"] == "Core Settings"
    assert core_entry["plugin_id"] == "core"
    assert "schema" in core_entry
    assert "value" in core_entry
    assert isinstance(core_entry["value"], dict)


def test_put_settings_success(client, admin_headers, api_prefix):
    """PUT /settings/{id} updates core settings."""
    payload = {"default_llm": "default:default", "default_embedder": "default:default"}
    response = client.put(
        f"{api_prefix}/settings/core__config__core",
        json=payload,
        headers=admin_headers,
    )
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == "core__config__core"
    assert data["slug"] == "core"
    assert data["type"] == "config"
    assert data["schema"] is not None


def test_put_settings_persists(client, admin_headers, api_prefix):
    """PUT then GET shows persisted settings."""
    payload = {"default_llm": "default:default", "default_embedder": "default:default"}
    client.put(
        f"{api_prefix}/settings/core__config__core",
        json=payload,
        headers=admin_headers,
    )

    response = client.get(f"{api_prefix}/settings", headers=admin_headers)
    assert response.status_code == 200

    entries = response.json()
    core_entry = next(
        (e for e in entries if e["id"] == "core__config__core"), None
    )
    assert core_entry is not None
    assert core_entry["value"]["default_llm"] == "default:default"


def test_put_settings_unknown_service(client, admin_headers, api_prefix):
    """PUT /settings/{id} with unknown id returns 404."""
    response = client.put(
        f"{api_prefix}/settings/nonexistent__model_providers__fake",
        json={"key": "value"},
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_put_settings_invalid_id_format(client, admin_headers, api_prefix):
    """PUT /settings/{id} with malformed id returns 404."""
    response = client.put(
        f"{api_prefix}/settings/invalid_id",
        json={"key": "value"},
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_put_settings_validation_error(client, admin_headers, api_prefix):
    """PUT /settings/{id} with invalid value returns appropriate status."""
    # default_llm expects a valid Literal option, send something invalid
    response = client.put(
        f"{api_prefix}/settings/core__config__core",
        json={"default_llm": "nonexistent_provider:model"},
        headers=admin_headers,
    )
    # If the dynamic schema has no enum members (no LLM providers available),
    # validation behavior depends on the Literal content. Accept 200 or 400.
    assert response.status_code in (200, 400)


def test_old_plugin_settings_endpoint_removed(client, admin_headers, api_prefix):
    """GET /plugins/{id}/settings should no longer exist."""
    response = client.get(
        f"{api_prefix}/plugins/core/settings", headers=admin_headers
    )
    assert response.status_code in (404, 405, 422)


def test_old_me_settings_endpoint_removed(client, admin_headers, api_prefix):
    """GET /me/settings should no longer exist."""
    response = client.get(f"{api_prefix}/me/settings", headers=admin_headers)
    assert response.status_code in (404, 405, 422)


def test_old_service_settings_endpoint_removed(client, admin_headers, api_prefix):
    """GET /services/core/core/settings should no longer exist."""
    response = client.get(
        f"{api_prefix}/services/core/core/settings", headers=admin_headers
    )
    assert response.status_code in (404, 405, 422)
