
from cat.looking_glass.stray_cat import StrayCat
from cat.auth.permissions import AuthUserInfo

from tests.utils import send_websocket_message


def test_session_creation_from_websocket(client):
    # send websocket message
    mex = {"text": "Where do I go?"}
    res = send_websocket_message(mex, client, user_id="Alice")

    # check response
    assert "You did not configure" in res["content"]

    # verify session
    strays = client.app.state.strays
    assert "Alice" in strays
    assert isinstance(strays["Alice"], StrayCat)
    assert strays["Alice"].user_id == "Alice"
    assert hasattr(strays["Alice"], "user_data")
    assert isinstance(strays["Alice"].user_data, AuthUserInfo)
    assert strays["Alice"].user_data.id == "Alice"
    convo = strays["Alice"].working_memory.history
    assert len(convo) == 2
    assert convo[0]["who"] == "Human"
    assert convo[0]["message"] == mex["text"]


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
    strays = client.app.state.strays
    assert "Alice" in strays
    assert isinstance(strays["Alice"], StrayCat)
    assert strays["Alice"].user_id == "Alice"
    convo = strays["Alice"].working_memory.history
    assert len(convo) == 0  # no ws message sent from Alice


# TODO: how do we test that:
# - session is coherent between ws and http calls
# - streaming happens
# - hooks receive the correct session

# REFACTOR TODO: we still do not delete sessions
