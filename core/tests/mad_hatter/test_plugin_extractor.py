import os
import shutil
from tests.utils import create_mock_plugin_zip
from cat.mad_hatter.plugin_extractor import PluginExtractor


# zip file contains just one folder, inside that folder we find the plugin
def test_unpackage_nested_zip(client):

    plugins_folder = "tests/mocks/mock_plugin_folder"
    
    zip_path = create_mock_plugin_zip()
    extractor = PluginExtractor(zip_path)
    extracted = extractor.extract(plugins_folder)
    assert extracted == plugins_folder + "/mock_plugin"
    assert os.path.exists(f"{plugins_folder}/mock_plugin")
    assert os.path.exists(f"{plugins_folder}/mock_plugin/mock_tool.py")
    
    os.remove(zip_path)
    shutil.rmtree(f"{plugins_folder}/mock_plugin")


# zip file does not contain a folder, but the plugin files directly
def test_unpackage_flat_zip(client):

    plugins_folder = "tests/mocks/mock_plugin_folder"
    
    zip_path = create_mock_plugin_zip(flat=True)
    extractor = PluginExtractor(zip_path)
    extracted = extractor.extract(plugins_folder)
    assert extracted == plugins_folder + "/mock_plugin"
    assert os.path.exists(f"{plugins_folder}/mock_plugin")
    assert os.path.exists(f"{plugins_folder}/mock_plugin/mock_tool.py")
    
    os.remove(zip_path)
    shutil.rmtree(f"{plugins_folder}/mock_plugin")


def test_get_id_and_extension(client):

    zip_path = create_mock_plugin_zip()
    extractor = PluginExtractor(zip_path)
    assert extractor.get_plugin_id() == "mock_plugin"
    assert extractor.get_extension() == "zip"
    os.remove(zip_path)


def test_raise_exception_if_a_wrong_extension_is_provided(client):
    try:
        PluginExtractor("./tests/infrastructure/plugin.wrong")
    except Exception as e:
        assert str(e) == "Invalid package extension. Valid extensions are: ['application/zip', 'application/x-tar']"

