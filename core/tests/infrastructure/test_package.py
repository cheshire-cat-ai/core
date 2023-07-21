from tests.utils import create_zip
from cat.infrastructure.package import Package

import os


def test_unpackage():
    zip_file_name = "mock_plugin"
    create_zip(f"tests/mocks/{zip_file_name}")
    zip = Package("./tests/mocks/mock_plugin.zip")
    zip.unpackage("./tests/infrastructure/")
    assert os.path.exists("./tests/infrastructure/mock_plugin")
    os.remove("tests/mocks/mock_plugin.zip")
    os.remove("./tests/infrastructure/mock_plugin/mock_tool.py")
    os.rmdir("./tests/infrastructure/mock_plugin")


def test_get_name():
    zip_file_name = "mock_plugin"
    create_zip(f"tests/mocks/{zip_file_name}")
    package = Package("./tests/mocks/mock_plugin.zip")
    assert package.get_name() == "mock_plugin.zip"
    os.remove("tests/mocks/mock_plugin.zip")


def test_get_extension():
    zip_file_name = "mock_plugin"
    create_zip(f"tests/mocks/{zip_file_name}")
    package = Package("./tests/mocks/mock_plugin.zip")
    assert package.get_extension() == "zip"
    os.remove("tests/mocks/mock_plugin.zip")


def test_raise_exception_if_a_wrong_extension_is_provided():
    try:
        Package("./tests/infrastructure/plugin.wrong")
    except Exception as e:
        assert str(e) == "Invalid package extension. Valid extensions are: ['application/zip', 'application/x-tar']"

