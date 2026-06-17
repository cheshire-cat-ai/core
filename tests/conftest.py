import time
import pytest
import pytest_asyncio
import os
from typing import Any, Generator

from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI
from fastapi.testclient import TestClient

from cat.looking_glass.stray_cat import StrayCat
from cat.auth import User
from cat.mad_hatter.plugin import Plugin
import cat.paths

from tests.utils import create_mock_plugin_zip


FAKE_TIMESTAMP = 1705855981


def clean_up_envs():
    # env variables
    os.environ["CCAT_DEBUG"] = "false" # do not autoreload


@pytest.fixture(scope="function")
def patches(monkeypatch, tmp_path):

    # scaffold directories
    (tmp_path / "mocks/data").mkdir(parents=True)
    (tmp_path / "mocks/plugins").mkdir()
    (tmp_path / "mocks/static").mkdir()

    # Use mock folder as project folder
    monkeypatch.setattr(
        cat.paths,
        'PROJECT_PATH',
        str(tmp_path / "mocks")
    )

    # TODOV2: maybe with uv this is fast enough
    # do not check plugin dependencies at every restart
    def mock_install_requirements(self, *args, **kwargs):
        pass
    monkeypatch.setattr(Plugin, "_install_requirements", mock_install_requirements)
    # TODOV2: this was in cleanups
    # installed with mock_plugin, here we uninstall
    #os.system("uv pip uninstall -y pip-install-test")


####################################
# Main fixture for the FastAPI app #
####################################
@pytest.fixture(scope="function")
def app(patches) -> Generator[FastAPI, Any, None]:
    
    clean_up_envs()
    from cat.startup import cheshire_cat_api # will instantiate the cat
    yield cheshire_cat_api
    clean_up_envs()


##############################
# Sync version of the client #
##############################
@pytest.fixture(scope="function")
def client(app) -> Generator[TestClient, Any, None]:
    """
    Create a new FastAPI TestClient.
    """
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
    yield { "Authorization": "Bearer meow"}

@pytest.fixture(scope="package")
def admin_query_params():
    yield { "token": "meow"}

# This fixture is useful to write tests in which
#   a plugin was just uploaded via http.
#   It wraps any test function having `just_installed_plugin` as an argument
@pytest.fixture(scope="function")
def just_installed_plugin(client, admin_headers):
    ### executed before each test function

    # create zip file with a plugin
    zip_path = create_mock_plugin_zip(flat=True)
    zip_file_name = zip_path.split("/")[-1]  # mock_plugin.zip in tests/mocks folder

    # upload plugin via endpoint
    with open(zip_path, "rb") as f:
        response = client.post(
            "/plugins/upload/",
            headers=admin_headers,
            files={"file": (zip_file_name, f, "application/zip")}
        )

    # request was processed
    assert response.status_code == 200
    assert response.json()["filename"] == zip_file_name

    ### each test function having `just_installed_plugin` as argument, is run here
    yield
    ###

    # clean up of zip file and mock_plugin_folder is done for every test automatically (see client fixture)


# fixture to have available an instance of StrayCat
@pytest.fixture(scope="function")
def stray(async_client):
    user = User(
        id="Alice",
        name="Alice"
    )
    stray_cat = StrayCat(user)
    # TODOV2: update to new data structure
    # TODOV2: remember mixin_init
    stray_cat.working_memory.user_message_json = {"user_id": user.id, "text": "meow"}
    yield stray_cat


#fixture for mock time.time function
@pytest.fixture(scope="function")
def patch_time_now(monkeypatch):

    def mytime():
        return FAKE_TIMESTAMP

    monkeypatch.setattr(time, 'time', mytime)

#fixture for mad hatter with mock plugin installed
@pytest.fixture(scope="function")
def mad_hatter_with_mock_plugin(client):  # client here injects the monkeypatched version of the cat

    # each test is given the mad_hatter instance
    mad_hatter = client.app.state.ccat.mad_hatter

    # install plugin
    new_plugin_zip_path = create_mock_plugin_zip(flat=True)
    mad_hatter.install_plugin(new_plugin_zip_path)

    yield mad_hatter

    # remove plugin (unless the test already removed it)
    if mad_hatter.plugin_exists("mock_plugin"):
        mad_hatter.uninstall_plugin("mock_plugin")
