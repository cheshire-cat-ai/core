import pytest
from cat.memory.working_memory import WorkingMemory

from tests.utils import send_websocket_message


def test_no_sessions_at_startup(client):
    
    for username in ["admin", "user", "Alice"]:
        wm = client.app.state.ccat.cache.get_value(f"{username}_working_memory")
        assert wm is None


@pytest.mark.parametrize("protocol", ["ws", "http"])
def test_session_creation(client, protocol):

    # send message
    mex = {"text": "Where do I go?"}
    if protocol == "ws":
        res = send_websocket_message(mex, client, user_id="Alice")
    else:
        res = client.post("/message", json=mex, headers={"user_id": "Alice"}).json()

    # check response
    assert res["user_id"] == "Alice"
    assert "You did not configure" in res["text"]

    # verify session
    wm = client.app.state.ccat.cache.get_value("Alice_working_memory")
    assert isinstance(wm, WorkingMemory)
    convo = wm.history
    assert len(convo) == 2
    assert convo[0]["who"] == "Human"
    assert convo[0].who == "Human"
    assert convo[0]["text"] == mex["text"]
    assert convo[0].text == mex["text"]
    assert convo[1]["who"] == "AI"
    assert convo[1].who == "AI"
    assert "You did not configure" in convo[1]["text"]
    assert "You did not configure" in convo[1].text


@pytest.mark.parametrize("protocol", ["ws", "http"])
def test_session_update(client, protocol):

    for message in range(5):

        # send message
        mex = {"text": str(message)}
        if protocol == "ws":
            res = send_websocket_message(mex, client, user_id="Caterpillar")
        else:
            res = client.post(
                "/message",
                json=mex,
                headers={"user_id": "Caterpillar"}
            ).json()

        # check response
        assert res["user_id"] == "Caterpillar"
        assert "You did not configure" in res["text"]

        # verify session
        wm = client.app.state.ccat.cache.get_value("Caterpillar_working_memory")
        assert isinstance(wm, WorkingMemory)
        assert len(wm.history) == int(message + 1) * 2 # user mex + reply
        for c_idx, c in enumerate(wm.history):
            if c_idx % 2 == 0:
                assert c.who == "Human"
                assert c.text == str(c_idx // 2)
            else:
                assert c.who == "AI"
                assert "You did not configure" in c.text


def test_session_sync_between_protocols(client):

    for message in range(5):

        # send messages alternating between ws and http
        mex = {"text": str(message)}
        if message % 2 == 0:
            res = send_websocket_message(mex, client, user_id="Caterpillar")
        else:
            res = client.post(
                "/message",
                json=mex,
                headers={"user_id": "Caterpillar"}
            ).json()

        # check response
        assert res["user_id"] == "Caterpillar"
        assert "You did not configure" in res["text"]

        # verify session
        wm = client.app.state.ccat.cache.get_value("Caterpillar_working_memory")
        assert isinstance(wm, WorkingMemory)
        assert len(wm.history) == int(message + 1) * 2 # user mex + reply
        for c_idx, c in enumerate(wm.history):
            if c_idx % 2 == 0:
                assert c.who == "Human"
                assert c.text == str(c_idx // 2)
            else:
                assert c.who == "AI"
                assert "You did not configure" in c.text


def test_session_sync_while_websocket_is_open(client):
    
    mex = {"text": "Oh dear!"}

    # keep open a websocket connection
    with client.websocket_connect("/ws/Alice") as websocket:
        # send ws message
        websocket.send_json(mex)
        # get reply
        res = websocket.receive_json()

    # checks
    wm = client.app.state.ccat.cache.get_value("Alice_working_memory")
    assert res["user_id"] == "Alice"
    assert len(wm.history) == 2
    #del wm

    # send another mex via http while ws connection is open
    res = client.post(
        "/message",
        json=mex,
        headers={"user_id": "Alice"}
    ).json()

    # checks
    assert res["user_id"] == "Alice"
    wm = client.app.state.ccat.cache.get_value("Alice_working_memory")
    assert len(wm.history) == 4

    # clear convo history via http
    res = client.delete("/memory/conversation_history", headers={"user_id": "Alice"})
    # checks
    assert res.status_code == 200
    wm = client.app.state.ccat.cache.get_value("Alice_working_memory")
    assert len(wm.history) == 0


# TODO: how do we test that:
# - streaming happens
# - hooks receive the correct session
# - sessions do not stay in memory forever

