from cat.infrastructure.zip import Zip
import os


def test_unzip():
    zip = Zip("./tests/infrastructure/plugin.zip")
    zip.unzip("./tests/infrastructure/")
    assert os.path.exists("./tests/infrastructure/plugin")
    os.remove("./tests/infrastructure/plugin")


def test_get_name():
    zip = Zip("./tests/infrastructure/plugin.zip")
    assert zip.get_name() == "plugin.zip"
