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


@pytest.mark.xfail(
    reason=(
        "FROZEN-CODE BUG: uploads/endpoints.py uses `config.API_URL`, which is not "
        "defined in cat.config (only `URL` exists). POST /api/v2/uploads and "
        "GET /api/v2/uploads therefore 500. Reported to maintainer; not fixed "
        "under the code freeze."
    ),
    strict=True,
)
def test_upload_file(client, admin_headers):
    files = {"file": ("hello.txt", b"hello cat", "text/plain")}
    response = client.post("/api/v2/uploads", headers=admin_headers, files=files)
    assert response.status_code == 200
