import os
import shutil
import pytest
from inspect import isfunction

from cat.mad_hatter.mad_hatter import MadHatter, Plugin
from cat.mad_hatter.decorators import CatHook, CatTool
from cat.looking_glass.cheshire_cat import CheshireCat

from tests.utils import create_mock_plugin_zip


# this function will be run before each test function
@pytest.fixture
def mad_hatter(client): # client here injects the monkeypatched version of the cat

    # setup before each unit
    cat = CheshireCat()
    mh = MadHatter(cat) # trygin out a fresh instance of the mad_hatter

    # each test is given a brand new instance
    yield mh


def test_instantiation_discovery(mad_hatter):

    assert isinstance(mad_hatter, MadHatter)
    
    # Mad Hatter finds core_plugin
    assert list(mad_hatter.plugins.keys()) == ["core_plugin"]
    assert isinstance(mad_hatter.plugins["core_plugin"], Plugin)
    assert "core_plugin" in mad_hatter.load_active_plugins_from_db()

    # finds hooks
    assert len(mad_hatter.hooks) > 0
    for h in mad_hatter.hooks:
        assert isinstance(h, CatHook)
        assert h.plugin_id == "core_plugin"
        assert type(h.name) == str
        assert isfunction(h.function)
        assert h.priority == 0.0

    # finds tool
    assert len(mad_hatter.tools) == 1
    tool = mad_hatter.tools[0]
    assert isinstance(tool, CatTool)
    assert tool.plugin_id == "core_plugin"
    assert isinstance(tool.cat, CheshireCat)
    assert tool.name == "get_the_time"
    assert "get_the_time" in tool.description
    assert "what time is it" in tool.docstring
    assert isfunction(tool.func)
    assert tool.return_direct == False
    assert tool.embedding is None # not embedded yet

    # list of active plugins in DB is correct
    active_plugins = mad_hatter.load_active_plugins_from_db()
    assert len(active_plugins) == 1
    assert active_plugins[0] == "core_plugin"


def test_plugin_install(mad_hatter: MadHatter):

    # install plugin
    new_plugin_zip_path = create_mock_plugin_zip()
    mad_hatter.install_plugin(new_plugin_zip_path)

    # archive extracted
    assert os.path.exists(
        os.path.join( mad_hatter.ccat.get_plugin_path(), "mock_plugin")
    )
    
    # plugins list updated
    assert list(mad_hatter.plugins.keys()) == ["core_plugin", "mock_plugin"]
    assert isinstance(mad_hatter.plugins["mock_plugin"], Plugin)
    assert "mock_plugin" in mad_hatter.load_active_plugins_from_db() # plugin starts active

    # plugin is activated by default
    assert len(mad_hatter.plugins["mock_plugin"].hooks) == 1
    assert len(mad_hatter.plugins["mock_plugin"].tools) == 1
    new_hook = mad_hatter.plugins["mock_plugin"].hooks[0]
    new_tool = mad_hatter.plugins["mock_plugin"].tools[0]

    # plugin reference
    assert new_hook.plugin_id == "mock_plugin"
    assert new_tool.plugin_id == "mock_plugin"

    # found tool and hook have been cached
    assert new_tool in mad_hatter.tools
    assert new_hook in mad_hatter.hooks

    # new hook has correct priority and has been sorted by mad_hatter as first
    assert new_hook.priority == 2
    assert id(new_hook) == id(mad_hatter.hooks[0]) # same object in memory!

    # tool has been embedded
    assert type(new_tool.embedding) == list
    assert len(new_tool.embedding) == 128 # fake embedder
    assert type(new_tool.embedding[0]) == float

    # list of active plugins in DB is correct
    active_plugins = mad_hatter.load_active_plugins_from_db()
    assert len(active_plugins) == 2
    assert "core_plugin" in active_plugins
    assert "mock_plugin" in active_plugins

    # remove plugin files (both zip and extracted)
    os.remove(new_plugin_zip_path)
    shutil.rmtree( os.path.join( mad_hatter.ccat.get_plugin_path(), "mock_plugin") )


def test_plugin_uninstall_non_existent(mad_hatter: MadHatter):

    # should not throw error
    assert len(mad_hatter.plugins) == 1 # core_plugin
    mad_hatter.uninstall_plugin("wrong_plugin")
    assert len(mad_hatter.plugins) == 1

    # list of active plugins in DB is correct
    active_plugins = mad_hatter.load_active_plugins_from_db()
    assert len(active_plugins) == 1
    assert active_plugins[0] == "core_plugin"


def test_plugin_uninstall(mad_hatter: MadHatter):

    # install plugin
    new_plugin_zip_path = create_mock_plugin_zip()
    mad_hatter.install_plugin(new_plugin_zip_path)

    # uninstall
    mad_hatter.uninstall_plugin("mock_plugin")

    # directory removed
    assert not os.path.exists(
        os.path.join( mad_hatter.ccat.get_plugin_path(), "mock_plugin")
    )
    
    # plugins list updated
    assert "mock_plugin" not in mad_hatter.plugins.keys()
    # plugin cache updated (only core_plugin stuff)
    assert len(mad_hatter.tools) == 1 # default tool
    for h in mad_hatter.hooks:
        assert h.plugin_id == "core_plugin"

    # list of active plugins in DB is correct
    active_plugins = mad_hatter.load_active_plugins_from_db()
    assert len(active_plugins) == 1
    assert active_plugins[0] == "core_plugin"

    # remove also original zip file
    os.remove(new_plugin_zip_path)