import pytest

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


def test_parse_json():

    json_string = """{
    "a": 2
}"""

    expected_json = {"a": 2}

    prefixed_json = "anything \n\t```json\n" + json_string
    assert( utils.parse_json(prefixed_json) == expected_json )

    suffixed_json = json_string + "\n``` anything"
    assert( utils.parse_json(suffixed_json) == expected_json )

    unclosed_json = """{"a":2"""
    assert( utils.parse_json(unclosed_json) == expected_json )

    unclosed_key_json = """{"a":2, "b":"""
    assert( utils.parse_json(unclosed_key_json) == expected_json )

    invalid_json = """yaml is better"""
    with pytest.raises(Exception) as e:
        utils.parse_json(invalid_json) == expected_json
    assert f"substring not found" in str(e.value)


# BaseModelDict to be deprecated in v2
def test_base_dict_model():

    class Origin(utils.BaseModelDict):
        location: str

    class Cat(utils.BaseModelDict):
        color: str
        origin: Origin

    origin = Origin(location="Cheshire")

    cat = Cat(color="pink", origin=origin)
    assert cat["color"] == cat.color == "pink"
    
    accesses = set([
        "Cheshire",
        cat.origin.location,
        cat.origin["location"],
        cat["origin"].location,
        cat["origin"]["location"],
        cat.get("origin").get("location")
    ])
    assert len(accesses) == 1

    # edit custom attributes
    cat.something = "meow"
    cat.origin.something = "meow"
    accesses = set([
        "meow",
        cat.something,
        cat["something"],
        cat.origin.something,
        cat["origin"]["something"],
        cat["origin"].something,
        cat.get("origin").get("something"),
        cat.get("missing", "meow"),
        cat.origin.get("missing", "meow")
    ])
    assert len(accesses) == 1

    # .keys()
    assert set(cat.keys()) == set(["color", "origin", "something"])
    assert set(cat.origin.keys()) == set(["location", "something"])

    # .values() # TODO: does not work recursively
    # print(cat.values())
    #for val in ["pink", "meow"]:
    #    assert val in set(cat.values())
    assert set(cat.origin.values()) == set(["Cheshire", "meow"])
    
    # in
    assert "color" in cat
    assert "location" in cat.origin
