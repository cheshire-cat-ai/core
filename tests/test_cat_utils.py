import os
from cat import config, utils


def test_get_base_url(client):
    assert config.URL == "http://localhost:1865"
    assert config.API_URL == "http://localhost:1865/api/v2/"


def test_get_base_path(client):
    assert config.BASE_PATH == os.getcwd() + "/src/cat"


def test_get_project_path(client):
    # during tests, project is in a temp folder
    pytest_tmp_folder = config.PROJECT_PATH
    assert pytest_tmp_folder.startswith("/tmp/pytest-")
    assert pytest_tmp_folder.endswith("/mocks")


def test_get_data_path(client):
    # "data" in production, "mocks/data" during tests
    assert config.DATA_PATH == os.path.join(config.PROJECT_PATH, "data")


def test_get_plugin_path(client):
    # "plugins" in production, "mocks/plugins" during tests
    assert config.PLUGINS_PATH == os.path.join(config.PROJECT_PATH, "plugins")


def test_get_uploads_path(client):
    # "uploads" in production, "mocks/uploads" during tests
    assert config.UPLOADS_PATH == os.path.join(config.DATA_PATH, "uploads")

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


