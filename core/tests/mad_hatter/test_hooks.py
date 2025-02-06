import pytest

from cat.mad_hatter.mad_hatter import MadHatter
from cat.mad_hatter.decorators import CatHook
from cat.convo.messages import CatMessage

from tests.utils import create_mock_plugin_zip


# this function will be run before each test function
@pytest.fixture(scope="function")
def mad_hatter(client):  # client here injects the monkeypatched version of the cat
    # each test is given the mad_hatter instance (it's a singleton)
    mad_hatter = MadHatter()

    # install plugin
    new_plugin_zip_path = create_mock_plugin_zip(flat=True)
    mad_hatter.install_plugin(new_plugin_zip_path)

    yield mad_hatter


def test_hook_discovery(mad_hatter):
    mock_plugin_hooks = mad_hatter.plugins["mock_plugin"].hooks

    assert len(mock_plugin_hooks) == 3
    for h in mock_plugin_hooks:
        assert isinstance(h, CatHook)
        assert h.plugin_id == "mock_plugin"


def test_hook_priority_execution(mad_hatter):
    fake_message = CatMessage(text="Priorities:", user_id="Alice")

    out = mad_hatter.execute_hook("before_cat_sends_message", fake_message, cat=None)
    assert out.text == "Priorities: priority 3 priority 2"
