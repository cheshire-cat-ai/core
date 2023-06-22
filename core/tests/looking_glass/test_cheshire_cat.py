from cat.looking_glass.cheshire_cat import CheshireCat

def test_get_base_url():
    cat = CheshireCat()
    assert cat.get_base_url() == "http://localhost:1865"

def test_get_base_path():
    cat = CheshireCat()
    assert cat.get_base_path() == "/app/cat/"

def test_get_plugin_path():
    cat = CheshireCat()
    assert cat.get_plugin_path() == "/app/cat/plugins/"

def test_get_static_url():
    cat = CheshireCat()
    assert cat.get_static_url() == "http://localhost:1865/static"