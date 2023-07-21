import os

from cat.mad_hatter.mad_hatter import MadHatter
from cat.looking_glass.cheshire_cat import CheshireCat
from tests.utils import create_mock_plugin_zip

from unittest.mock import MagicMock
from unittest.mock import patch

'''
def test_install_plugin():
    ccat = CheshireCat()
    ccat.get_plugin_path = MagicMock(return_value="./tests/mad_hatter/plugin_folder")
    ccat.bootstrap = MagicMock()
    mad_hatter = MadHatter(ccat)

    zip_file_name = "mock_plugin"
    create_zip(f"tests/mocks/{zip_file_name}")
    with patch('importlib.import_module'):
        mad_hatter.install_plugin("tests/mocks/mock_plugin.zip")
        ccat.get_plugin_path.assert_called_once()
        ccat.bootstrap.assert_called_once()

    os.remove("tests/mocks/mock_plugin.zip")

    # cleanup folder
    os.remove("./tests/mad_hatter/plugin_folder/mock_plugin/mock_tool.py")
    os.rmdir("./tests/mad_hatter/plugin_folder/mock_plugin")
'''