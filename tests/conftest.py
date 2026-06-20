# ---------------------------------------------------------------------------
# Core suite conftest.
#
# Per-test isolation, the `with_plugins` selector, and the shared fixtures
# (`app`, `client`/`async_client` — authenticated as admin by default — and
# `anon_client`) live in the core pytest plugin `cat.testing` (registered via a
# pytest11 entry point), so the core suite and every plugin suite share them with
# no duplication. This file only adds fixtures specific to the core suite.
# ---------------------------------------------------------------------------
import os

import pytest
import pytest_asyncio

from cat.ambient.runtime import ccat  # the one CheshireCat instance per process

from tests.utils import create_mock_plugin_zip


# The mock plugin installed two ways, mirroring the two install paths in core:

# 1) via HTTP — uploaded through the real POST /plugins endpoint.
@pytest.fixture(scope="function")
def just_installed_plugin(client):
    zip_path = create_mock_plugin_zip(flat=True)
    zip_file_name = os.path.basename(zip_path)  # mock_plugin.zip

    with open(zip_path, "rb") as f:
        response = client.post(
            "/plugins",
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
    mad_hatter = ccat().mad_hatter

    new_plugin_zip_path = create_mock_plugin_zip(flat=True)
    await mad_hatter.install_plugin(new_plugin_zip_path)

    yield mad_hatter
    # no teardown needed: each test runs in its own throwaway project folder
