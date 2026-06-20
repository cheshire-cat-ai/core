"""Uploads plugin suite.

Lives in the plugin, so the harness auto-includes `uploads` (core + uploads) for
every test here — no need to name the plugin. The uploads endpoints are mounted
under `/api/v2/uploads`.
"""

import os

import pytest

from cat import config


def test_serve_nonexistent_file(client):
    """GET a file that isn't there → 404 (serving endpoint is open)."""
    response = client.get("/api/v2/uploads/Meooow.txt")
    assert response.status_code == 404


def test_serve_existing_file(client):
    """A file present under UPLOADS_PATH is served back."""
    file_name = "Meooow.txt"
    file_path = os.path.join(config.UPLOADS_PATH, file_name)

    # before: not there
    assert client.get(f"/api/v2/uploads/{file_name}").status_code == 404

    os.makedirs(config.UPLOADS_PATH, exist_ok=True)
    with open(file_path, "w") as f:
        f.write("Meow")

    response = client.get(f"/api/v2/uploads/{file_name}")
    assert response.status_code == 200
    assert response.text == "Meow"


def test_upload_then_list(client, admin_headers):
    """Upload a file, then it shows up in the per-user listing."""
    files = {"file": ("hello.txt", b"hello cat", "text/plain")}
    response = client.post("/api/v2/uploads", headers=admin_headers, files=files)
    assert response.status_code == 200, response.text

    body = response.json()
    assert body["mime_type"] == "text/plain"
    assert "uploads/" in body["url"]
    assert body["url"].startswith(config.URL)

    # it appears in the authenticated user's upload listing
    listing = client.get("/api/v2/uploads", headers=admin_headers)
    assert listing.status_code == 200
    assert any(u["url"].endswith("hello.txt") for u in listing.json())
