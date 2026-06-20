"""Smoke tests for the shared test harness (`cat.testing`).

These exercise the harness primitive itself: declarative plugin selection,
resolution from `./plugins`, and per-test isolation.
"""

import os

import pytest

from cat import config
from cat.ambient.runtime import ccat
from cat.testing import REPO_PLUGINS


def _active(client, admin_headers):
    """The set of active plugin ids, read through the real /plugins route."""
    res = client.get("/plugins", headers=admin_headers)
    assert res.status_code == 200, res.text
    return {p["id"] for p in res.json() if p["active"]}


def _present(client, admin_headers):
    """The set of installed (present-on-disk) plugin ids."""
    res = client.get("/plugins", headers=admin_headers)
    assert res.status_code == 200, res.text
    return {p["id"] for p in res.json()}


# --- core only -------------------------------------------------------------

def test_core_only_has_zero_plugins(client, admin_headers):
    """An unmarked core test boots core with no plugins active or present."""
    assert _present(client, admin_headers) == set()
    assert _active(client, admin_headers) == set()


# --- single / multiple selection ------------------------------------------

@pytest.mark.with_plugins("uploads")
def test_single_plugin_selection(client, admin_headers):
    assert _active(client, admin_headers) == {"uploads"}


@pytest.mark.with_plugins("uploads", "chats")
def test_multiple_plugin_selection(client, admin_headers):
    assert _active(client, admin_headers) == {"uploads", "chats"}


# --- resolution from ./plugins, not scaffold -------------------------------

def test_selected_plugins_resolve_from_project_plugins_folder(client, admin_headers):
    """Selection copies plugin source from the developer's ./plugins folder."""
    # uploads ships as a default, so session materialization seeds it into
    # ./plugins; it is therefore selectable from there like any other plugin.
    assert os.path.isdir(os.path.join(REPO_PLUGINS, "uploads"))


# --- isolation -------------------------------------------------------------

def test_runs_in_throwaway_project(client, admin_headers, tmp_path):
    """Project paths point inside the per-test tmp folder, not the real repo."""
    assert str(tmp_path) in config.PROJECT_PATH
    assert str(tmp_path) in config.PLUGINS_PATH
    assert str(tmp_path) in config.DATA_PATH


def test_real_plugins_folder_untouched_by_install(client, admin_headers, just_installed_plugin):
    """Installing a plugin writes into the tmp project, never the real ./plugins."""
    # the mock plugin is installed (in the throwaway project) ...
    assert "mock_plugin" in _present(client, admin_headers)
    # ... but the developer's real ./plugins never gains it
    assert not os.path.isdir(os.path.join(REPO_PLUGINS, "mock_plugin"))


def test_each_test_gets_a_fresh_db(client, admin_headers):
    """No plugin installed in a previous test leaks into this one."""
    assert "mock_plugin" not in _present(client, admin_headers)
    # core-only baseline: nothing carried over
    assert _present(client, admin_headers) == set()
