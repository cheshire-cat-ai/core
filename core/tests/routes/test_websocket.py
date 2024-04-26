
from cat.log import log

from tests.utils import send_websocket_message, send_n_websocket_messages
from tests.routes.plugins.fixture_just_installed_plugin import just_installed_plugin


def check_correct_websocket_reply(reply):
    for k in ["type", "content", "why"]:
        assert k in reply.keys()

    assert reply["type"] != "error"
    assert type(reply["content"]) == str
    assert "You did not configure" in reply["content"]
    assert len(reply["why"].keys()) > 0
      

def test_websocket(client):

        # send websocket message
        res = send_websocket_message({
            "text": "It's late! It's late"
        }, client)

        check_correct_websocket_reply(res)


def test_websocket_multiple_messages(client):

        # send websocket message
        replies = send_n_websocket_messages(3, client)

        for res in replies:
            check_correct_websocket_reply(res)
