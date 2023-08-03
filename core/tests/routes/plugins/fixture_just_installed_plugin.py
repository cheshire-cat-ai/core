import time
import os
import shutil
import pytest
from tests.utils import create_mock_plugin_zip

# This fixture is useful to write tests in which
#   a plugin was just uploaded via http.
#   It wraps any test function having `just_installed_plugin` as an argument
@pytest.fixture()
def just_installed_plugin(client):

    ### executed before each test function

    # create zip file with a plugin
    zip_path = create_mock_plugin_zip()
    zip_file_name = zip_path.split("/")[-1] # mock_plugin.zip in tests/mocks folder

    # upload plugin via endpoint
    with open(zip_path, "rb") as f:
        response = client.post(
            "/plugins/upload/",
            files={
                "file": (zip_file_name, f, "application/zip")
            }
        )

    # request was processed
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["filename"] == zip_file_name

    ### each test function having `just_installed_plugin` as argument, is run here
    yield
    ###

    ### executed after each test function
    # delete zip from tests folder
    os.remove(zip_path)
    # remove plugin folder in mock_plugin_folder
    mock_plugin_folder = "tests/mocks/mock_plugin_folder/mock_plugin"
    if os.path.exists(mock_plugin_folder):
        shutil.rmtree(mock_plugin_folder)
