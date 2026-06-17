# TODOV2: new tests for the session once the cat is stateless
#import time
#import os
import pytest
from cat.memory.working_memory import WorkingMemory

from tests.utils import send_http_message


# only valid for in_memory cache
def test_no_sessions_at_startup(client):

    for username in ["admin", "user", "Alice"]:
        wm = client.app.state.ccat.cache.get_value(f"{username}_working_memory")
        assert wm is None


def test_session_creation_http(client, admin_headers):

    # send message
    mex = "Where do I go?"
    admin_headers["user_id"] = "Alice"
    res = send_http_message(mex, client, headers=admin_headers)

    # check response
    assert res["user_id"] == "Alice"
    assert "You did not configure" in res["text"]

    # verify session
    wm = client.app.state.ccat.cache.get_value("Alice_working_memory")
    assert isinstance(wm, WorkingMemory)


# TODOV2: how do we test that:
# - streaming happens
