import os
from cat.memory.working_memory import WorkingMemory

from tests.utils import send_websocket_message


def test_no_sessions_at_startup(client):
    
    for username in ["admin", "user", "Alice"]:
        wm = client.app.state.ccat.cache.get_value(f"{username}_working_memory")
        assert wm is None


def test_session_creation_from_websocket(client):
    # send websocket message
    mex = {"text": "Where do I go?"}
    res = send_websocket_message(mex, client, user_id="Alice")

    # check response
    assert "You did not configure" in res["content"]

    # verify session
    wm = client.app.state.ccat.cache.get_value("Alice_working_memory")
    assert isinstance(wm, WorkingMemory)
    convo = wm.history
    assert len(convo) == 2
    assert convo[0]["who"] == "Human"
    assert convo[0]["text"] == mex["text"]
    assert convo[1]["who"] == "AI"
    assert "You did not configure" in convo[1]["text"]


def test_session_update_from_websocket(client):

    for message in range(1,5):

        # message
        res = send_websocket_message(
            {"text": message}, client, user_id="Alice"
        )

        # check response
        assert "You did not configure" in res["content"]

        # verify session
        wm = client.app.state.ccat.cache.get_value("Alice_working_memory")
        assert isinstance(wm, WorkingMemory)
        convo = wm.history
        assert len(convo) == int(message) * 2 # user mex + reply
        for c_idx, c in enumerate(convo):
            if c_idx % 2 == 0:
                assert c["who"] == "Human"
                assert c["text"] == str(c_idx//2 + 1)
            else:
                assert c["who"] == "AI"
                assert "You did not configure" in c["text"]


def test_session_creation_from_http(client):
    content_type = "text/plain"
    file_name = "sample.txt"
    file_path = f"tests/mocks/{file_name}"
    with open(file_path, "rb") as f:
        files = {"file": (file_name, f, content_type)}

        # sending file from Alice
        response = client.post(
            "/rabbithole/", files=files, headers={"user_id": "Alice"}
        )

    # check response
    assert response.status_code == 200

    # verify session
    wm = client.app.state.ccat.cache.get_value("Alice_working_memory")
    assert isinstance(wm, WorkingMemory)
    assert len(wm.history) == 0  # no messages sent or received


# TODO: how do we test that:
# - session is coherent between ws and http calls
# - streaming happens
# - hooks receive the correct session
# - sessions do not stay in memory forever

