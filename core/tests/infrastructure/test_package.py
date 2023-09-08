import os
import shutil
from tests.utils import create_mock_plugin_zip
from cat.mad_hatter.plugin_extractor import PluginExtractor


def test_unpackage(client):

    plugin_folder = "tests/mocks/mock_plugin_folder"
    
    zip_path = create_mock_plugin_zip()
    extractor = PluginExtractor(zip_path)
    extracted = extractor.extract(plugin_folder)
    assert len(extracted) == 1
    assert extracted[0] == "mock_plugin"
    assert os.path.exists(f"{plugin_folder}/mock_plugin")
    assert os.path.exists(f"{plugin_folder}/mock_plugin/mock_tool.py")
    
    os.remove(zip_path)
    shutil.rmtree(f"{plugin_folder}/mock_plugin")


def test_get_name_and_extension(client):

    zip_path = create_mock_plugin_zip()
    extractor = PluginExtractor(zip_path)
    assert extractor.get_name() == "mock_plugin.zip"
    assert extractor.get_extension() == "zip"
    os.remove(zip_path)


def test_raise_exception_if_a_wrong_extension_is_provided(client):
    try:
        PluginExtractor("./tests/infrastructure/plugin.wrong")
    except Exception as e:
        assert str(e) == "Invalid package extension. Valid extensions are: ['application/zip', 'application/x-tar']"

