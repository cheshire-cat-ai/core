import os
from tests.utils import create_mock_plugin_zip
from cat.infrastructure.package import Package


def test_unpackage():
    
    zip_path = create_mock_plugin_zip()
    zip = Package(zip_path)
    zip.unpackage("tests/infrastructure/")
    assert os.path.exists("tests/infrastructure/mock_plugin")
    assert os.path.exists("tests/infrastructure/mock_plugin/mock_tool.py")
    
    os.remove(zip_path)
    os.remove("tests/infrastructure/mock_plugin/mock_tool.py")
    os.rmdir("tests/infrastructure/mock_plugin")


def test_get_name_and_extension():

    zip_path = create_mock_plugin_zip()
    zip = Package(zip_path)
    assert zip.get_name() == "mock_plugin.zip"
    assert zip.get_extension() == "zip"
    os.remove(zip_path)


def test_raise_exception_if_a_wrong_extension_is_provided():
    try:
        Package("./tests/infrastructure/plugin.wrong")
    except Exception as e:
        assert str(e) == "Invalid package extension. Valid extensions are: ['application/zip', 'application/x-tar']"

