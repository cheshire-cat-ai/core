
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


"""
# this test runs with mock_plugin already installed
def test_websocket_error_sending_message_without_waiting(client, just_installed_plugin):

        # use fake LLM
        response = client.put("/llm/settings/FakeTestLLMConfig", json={})
        assert response.status_code == 200

        # send websocket message
        user_id = "Alice"
        message = {
            "text": "It's late! It's late"
        }

        # send messages without waiting for a reply
        with client.websocket_connect(f"/ws/{user_id}") as websocket:
            
            # sed ws message
            websocket.send_json(message)

            # send another (no websocket.receive_json())
            websocket.send_json(message)
            #assert False # should throw error
"""