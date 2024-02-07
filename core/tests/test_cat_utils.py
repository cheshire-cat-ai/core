from cat import utils


def test_get_base_url():
    assert utils.get_base_url() == 'http://localhost:1865/'


def test_get_base_path():
    assert utils.get_base_path() == 'cat/'


def test_get_plugin_path():
    # plugin folder is "cat/plugins/" in production, "tests/mocks/mock_plugin_folder/" during tests
    # assert utils.get_plugins_path() == 'cat/plugins/'
    assert utils.get_plugins_path() == 'tests/mocks/mock_plugin_folder/'


def test_get_static_path():
    assert utils.get_static_path() == 'cat/static/'


def test_get_static_url():
    assert utils.get_static_url() == 'http://localhost:1865/static/'


def test_levenshtein_distance():
    assert utils.levenshtein_distance("hello world", "hello world") == 0.0
    assert utils.levenshtein_distance("hello world", "") == 1.0
