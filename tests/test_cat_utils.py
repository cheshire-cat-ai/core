import os
import pytest
from cat import urls, paths, utils


def test_get_base_url(client):
    # TODOV2: update to new env var CCAT_URL
    assert urls.BASE_URL == "http://localhost:1865"
    # test when CCAT_CORE_USE_SECURE_PROTOCOLS is set
    os.environ["CCAT_CORE_USE_SECURE_PROTOCOLS"] = "1"
    assert urls.BASE_URL == "https://localhost:1865"
    os.environ["CCAT_CORE_USE_SECURE_PROTOCOLS"] = "0"
    assert urls.BASE_URL == "http://localhost:1865"
    os.environ["CCAT_CORE_USE_SECURE_PROTOCOLS"] = ""
    assert urls.BASE_URL == "http://localhost:1865"


# TODOV2: check get_api_url()


def test_get_base_path(client):
    assert paths.BASE_PATH == os.getcwd() + "/src/cat"


def test_get_project_path(client):
    # during tests, project is in a temp folder
    pytest_tmp_folder = paths.PROJECT_PATH
    assert pytest_tmp_folder.startswith("/tmp/pytest-")
    assert pytest_tmp_folder.endswith("/mocks")


def test_get_data_path(client):
    # "data" in production, "mocks/data" during tests
    assert paths.DATA_PATH == os.path.join(paths.PROJECT_PATH, "data")


def test_get_plugin_path(client):
    # "plugins" in production, "mocks/plugins" during tests
    assert paths.PLUGINS_PATH == os.path.join(paths.PROJECT_PATH, "plugins")


def test_get_uploads_path(client):
    # "uploads" in production, "mocks/uploads" during tests
    assert paths.UPLOADS_PATH == os.path.join(paths.DATA_PATH, "uploads")

def test_levenshtein_distance():
    # identical strings → 0
    assert utils.levenshtein_distance("cat", "cat") == 0.0
    # both empty → 0
    assert utils.levenshtein_distance("", "") == 0.0
    # one empty → 1
    assert utils.levenshtein_distance("cat", "") == 1.0
    assert utils.levenshtein_distance("", "cat") == 1.0
    # completely different same-length strings → 1
    assert utils.levenshtein_distance("abc", "xyz") == 1.0
    # single substitution: "cat" → "bat" = 1 edit / 3 chars = 0.333...
    assert round(utils.levenshtein_distance("cat", "bat"), 3) == round(1 / 3, 3)
    # classic example: "kitten" → "sitting" = 3 edits / 7 chars ≈ 0.429
    assert round(utils.levenshtein_distance("kitten", "sitting"), 3) == round(3 / 7, 3)
    # symmetry
    assert utils.levenshtein_distance("abc", "ab") == utils.levenshtein_distance("ab", "abc")


