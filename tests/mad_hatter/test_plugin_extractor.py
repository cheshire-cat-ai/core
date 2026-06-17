import os
import shutil
import pytest

from cat.mad_hatter.plugin_extractor import PluginExtractor
from cat import paths
from tests.utils import create_mock_plugin_zip


# plugin_is_flat is False: zip file contains just one folder, inside that folder we find the plugin
# plugin_is_flat is True: zip file does not contain a folder, but the plugin files directly
@pytest.mark.parametrize("plugin_is_flat", [True, False])
def test_unpackage_zip(client, plugin_is_flat):
    plugins_folder = paths.PLUGINS_PATH

    zip_path = create_mock_plugin_zip(flat=plugin_is_flat)
    extractor = PluginExtractor(zip_path)
    extracted = extractor.extract(plugins_folder)
    assert extracted == plugins_folder + "/mock_plugin"
    assert os.path.exists(f"{plugins_folder}/mock_plugin")
    assert os.path.exists(f"{plugins_folder}/mock_plugin/mock_tool.py")

    os.remove(zip_path)
    shutil.rmtree(f"{plugins_folder}/mock_plugin")


@pytest.mark.parametrize("plugin_is_flat", [True, False])
def test_get_id_and_extension(client, plugin_is_flat):
    zip_path = create_mock_plugin_zip(flat=plugin_is_flat)
    extractor = PluginExtractor(zip_path)
    assert extractor.id == "mock_plugin"
    assert extractor.extension == "zip"
    os.remove(zip_path)


def test_raise_exception_if_a_wrong_extension_is_provided(client):
    try:
        PluginExtractor("./tests/infrastructure/plugin.wrong")
    except Exception as e:
        assert (
            str(e)
            == "Invalid package extension. Valid extensions are: ['application/zip', 'application/x-tar']"
        )
