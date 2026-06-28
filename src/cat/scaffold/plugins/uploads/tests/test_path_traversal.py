"""Regression test: path traversal must not escape ``UPLOADS_PATH``.

The serving endpoint ``GET /uploads/{path:path}`` joins the URL path parameter
to ``config.UPLOADS_PATH`` without normalisation or containment. The route is
unauthenticated (no ``role=`` gate). Raw ``..`` segments are normalised by the
HTTP client and Starlette, but URL-encoded equivalents (e.g. ``%2e%2e``,
``..%2f``) pass through to the handler and reach ``FileResponse``, leaking
files from outside the uploads directory.
"""

import os

import pytest

from cat import config


# Encoded traversal vectors that survive client/Starlette normalisation and
# previously reached the FileResponse sink.
_TRAVERSAL_VECTORS = [
    "%2e%2e/secret.txt",
    "%2e%2e%2fsecret.txt",
    "..%2fsecret.txt",
    ".%2e/secret.txt",
    "%2e./secret.txt",
]


@pytest.fixture
def secret_above_uploads():
    """Plant a secret one directory above ``UPLOADS_PATH`` and clean it up."""
    os.makedirs(config.UPLOADS_PATH, exist_ok=True)
    # DATA_PATH is the parent of UPLOADS_PATH in the default layout.
    secret_path = os.path.join(config.DATA_PATH, "secret.txt")
    secret = "the-cat-knows-too-much"
    with open(secret_path, "w") as f:
        f.write(secret)
    try:
        yield secret_path, secret
    finally:
        if os.path.exists(secret_path):
            os.remove(secret_path)


@pytest.mark.parametrize("vector", _TRAVERSAL_VECTORS)
def test_uploads_get_rejects_encoded_path_traversal(
    anon_client, secret_above_uploads, vector
):
    """Encoded ``..`` traversal must not return files outside UPLOADS_PATH."""
    _, secret = secret_above_uploads
    response = anon_client.get(f"/uploads/{vector}")
    assert response.status_code != 200, (
        f"Path traversal leaked file via {vector!r} "
        f"(status={response.status_code}, body={response.text!r})"
    )
    assert secret not in response.text


def test_uploads_get_serves_legitimate_file(anon_client):
    """A real file inside UPLOADS_PATH must still be served after the fix."""
    os.makedirs(config.UPLOADS_PATH, exist_ok=True)
    file_path = os.path.join(config.UPLOADS_PATH, "ok.txt")
    with open(file_path, "w") as f:
        f.write("hi")
    try:
        response = anon_client.get("/uploads/ok.txt")
        assert response.status_code == 200
        assert response.text == "hi"
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


def test_uploads_get_rejects_absolute_path(anon_client):
    """An absolute path in the parameter must not escape UPLOADS_PATH either.

    ``os.path.join('/uploads/dir', '/etc/passwd')`` returns ``/etc/passwd`` —
    a classic pitfall ``os.path.realpath`` containment also closes.
    """
    # Plant a known-safe sentinel outside UPLOADS_PATH; check it does not leak.
    sentinel = os.path.join(config.DATA_PATH, "abs_secret.txt")
    with open(sentinel, "w") as f:
        f.write("absolute-secret")
    try:
        # ``//`` collapses to ``/`` so Starlette routes this to the parameterised
        # endpoint with ``path == config.DATA_PATH + "/abs_secret.txt"``.
        response = anon_client.get(f"/uploads/{sentinel.lstrip('/')}".replace("//", "/"))
        # Acceptable outcomes: not found, forbidden, or the same path resolved
        # *inside* UPLOADS_PATH (which won't exist) — never the planted secret.
        assert "absolute-secret" not in response.text
    finally:
        if os.path.exists(sentinel):
            os.remove(sentinel)
