from cat.infrastructure.package import Package
import os


def test_unpackage():
    zip = Package("./tests/infrastructure/plugin.zip")
    zip.unpackage("./tests/infrastructure/")
    assert os.path.exists("./tests/infrastructure/plugin")
    os.remove("./tests/infrastructure/plugin")


def test_get_name():
    package = Package("./tests/infrastructure/plugin.zip")
    assert package.get_name() == "plugin.zip"

def test_get_extension():
    package = Package("./tests/infrastructure/plugin.zip")
    assert package.get_extension() == "zip"

def test_raise_exception_if_a_wrong_extension_is_provided():
    try:
        Package("./tests/infrastructure/plugin.wrong")
    except Exception as e:
        assert str(e) == "Invalid package extension. Valid extensions are: ['.zip', '.tar']"