import os

from cat.mad_hatter.mad_hatter import MadHatter
from cat.looking_glass.cheshire_cat import CheshireCat


from unittest.mock import MagicMock
from unittest.mock import patch

def test_install_plugin():
    ccat = CheshireCat()
    ccat.get_plugin_path = MagicMock(return_value="./tests/mad_hatter/plugin_folder")
    ccat.bootstrap = MagicMock()
    mad_hatter = MadHatter(ccat)

    with patch('importlib.import_module'):
        mad_hatter.install_plugin("./tests/mad_hatter/plugin_test.zip")
        ccat.get_plugin_path.assert_called_once()
        ccat.bootstrap.assert_called_once()

    # cleanup folder
    os.remove("./tests/mad_hatter/plugin_folder/plugin_test/plugin.py")
    os.rmdir("./tests/mad_hatter/plugin_folder/plugin_test")

