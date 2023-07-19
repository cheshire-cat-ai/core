import shutil

from cat.infrastructure.package import Package
import os


def test_unpackage():
    create_zip()
    zip = Package("./tests/mocks/mock_plugin.zip")
    zip.unpackage("./tests/infrastructure/")
    assert os.path.exists("./tests/infrastructure/mock_plugin")
    delete_zip()
    os.remove("./tests/infrastructure/mock_plugin/mock_tool.py")
    os.rmdir("./tests/infrastructure/mock_plugin")


def test_get_name():
    create_zip()
    package = Package("./tests/mocks/mock_plugin.zip")
    assert package.get_name() == "mock_plugin.zip"
    delete_zip()


def test_get_extension():
    create_zip()
    package = Package("./tests/mocks/mock_plugin.zip")
    assert package.get_extension() == "zip"
    delete_zip()


def test_raise_exception_if_a_wrong_extension_is_provided():
    try:
        Package("./tests/infrastructure/plugin.wrong")
    except Exception as e:
        assert str(e) == "Invalid package extension. Valid extensions are: ['application/zip', 'application/x-tar']"


def create_zip():
    zip_file_name = "mock_plugin"
    zip_path = f"tests/mocks/{zip_file_name}"
    shutil.make_archive(
        zip_path,
        "zip",
        root_dir="tests/mocks/",
        base_dir="mock_plugin"
    )
    return zip_path


def delete_zip():
    zip_file_name = "mock_plugin.zip"
    zip_path = f"tests/mocks/{zip_file_name}"
    os.remove(zip_path)
