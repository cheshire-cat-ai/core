# ---------------------------------------------------------------------------
# Every test runs in its own fresh project folder, so nothing accumulates
# between tests (installed plugins, DB rows, uploads) and the developer's real
# ./data and ./plugins are never touched.
#
# Importing `cat` no longer touches the filesystem — the DB engine path is fixed
# at import, but folders/tables are materialized by `scaffolder.setup_project()`.
# So each test just repoints the process-wide engine at its own folder and
# scaffolds it, exactly like running `ccat` in an empty directory.
# ---------------------------------------------------------------------------
import os
import time
from typing import Any, Generator

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI
from fastapi.testclient import TestClient

from cat import config
from cat.context import app as cat_app  # aliased: `app` is also a fixture name below
from cat.mad_hatter.plugin import Plugin
from cat.scaffold import scaffolder
from cat.db.database import DB as db_engine

from tests.utils import create_mock_plugin_zip


FAKE_TIMESTAMP = 1705855981


@pytest.fixture(scope="function", autouse=True)
def patches(monkeypatch, tmp_path):
    # Per-test isolated project folder ("mocks" mirrors a real project layout).
    mocks = tmp_path / "mocks"
    monkeypatch.setitem(config._values, "PROJECT_PATH", str(mocks))
    monkeypatch.setitem(config._values, "PLUGINS_PATH", str(mocks / "plugins"))
    monkeypatch.setitem(config._values, "DATA_PATH", str(mocks / "data"))
    monkeypatch.setitem(config._values, "UPLOADS_PATH", str(mocks / "data" / "uploads"))

    # do not check plugin dependencies on every (re)install during tests
    monkeypatch.setattr(Plugin, "_install_requirements", lambda self, *a, **k: None)

    # Point the process-wide SQLite engine at this test's own db file. The engine
    # opens a fresh connection per query, so flipping `.path` redirects every
    # read/write for this test.
    monkeypatch.setattr(db_engine, "path", str(mocks / "data" / "core" / "core.db"))

    # Scaffold the fresh project (folders + db/tables + seeded settings) — the
    # same thing `cat.main.main()` does before launching the server.
    scaffolder.setup_project()


####################################
# Main fixture for the FastAPI app #
####################################
@pytest.fixture(scope="function")
def app() -> Generator[FastAPI, Any, None]:
    # a fresh app per test (isolated routes + lifespan); see startup.create_app
    from cat.startup import create_app
    yield create_app()


##############################
# Sync version of the client #
##############################
@pytest.fixture(scope="function")
def client(app) -> Generator[TestClient, Any, None]:
    """Create a new FastAPI TestClient."""
    with TestClient(app) as client:
        yield client


###############################
# Async version of the client #
###############################
@pytest_asyncio.fixture(scope="function")
async def async_client(app):
    async with LifespanManager(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            yield ac


@pytest.fixture(scope="package")
def admin_headers():
    yield {"Authorization": "Bearer meow"}


@pytest.fixture(scope="package")
def admin_query_params():
    yield {"token": "meow"}


# fixture for mock time.time function
@pytest.fixture(scope="function")
def patch_time_now(monkeypatch):
    def mytime():
        return FAKE_TIMESTAMP

    monkeypatch.setattr(time, "time", mytime)


# The mock plugin installed two ways, mirroring the two install paths in core:

# 1) via HTTP — uploaded through the real POST /api/v2/plugins endpoint.
@pytest.fixture(scope="function")
def just_installed_plugin(client, admin_headers):
    zip_path = create_mock_plugin_zip(flat=True)
    zip_file_name = os.path.basename(zip_path)  # mock_plugin.zip

    with open(zip_path, "rb") as f:
        response = client.post(
            "/plugins",
            headers=admin_headers,
            files={"file": (zip_file_name, f, "application/zip")},
        )

    assert response.status_code == 200, response.text
    assert response.json()["id"] == "mock_plugin"

    yield
    # no teardown needed: each test runs in its own throwaway project folder


# 2) via MadHatter directly — install_plugin is async in v2, so this is an
#    async fixture bootstrapped through async_client.
@pytest_asyncio.fixture(scope="function")
async def mad_hatter_with_mock_plugin(async_client):
    mad_hatter = cat_app().mad_hatter

    new_plugin_zip_path = create_mock_plugin_zip(flat=True)
    await mad_hatter.install_plugin(new_plugin_zip_path)

    yield mad_hatter
    # no teardown needed: each test runs in its own throwaway project folder
