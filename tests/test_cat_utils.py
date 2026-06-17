import os
import tempfile
from cat import config, utils


def test_get_base_url(client):
    assert config.URL == "http://localhost:1865"


def test_get_base_path(client):
    # BASE_PATH is the installed package dir, independent of the cwd
    assert config.BASE_PATH.endswith("/src/cat")


def test_get_project_path(client):
    # during tests, each test gets its own temp project folder (see conftest)
    pytest_tmp_folder = config.PROJECT_PATH
    assert pytest_tmp_folder.startswith(tempfile.gettempdir())
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


