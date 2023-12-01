
from cat import utils

def test_get_base_url():
    assert utils.get_base_url() == "http://localhost:1865/"

def test_get_base_path():
    assert utils.get_base_path() == "cat/"

def test_get_plugin_path():
    assert utils.get_plugins_path() == "cat/plugins/"

def test_get_static_path():
    assert utils.get_static_path() == "cat/static/"

def test_get_static_url():
    assert utils.get_static_url() == "http://localhost:1865/static/"

