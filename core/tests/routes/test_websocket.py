import time
from tests.utils import send_websocket_message, send_n_websocket_messages


def check_correct_websocket_reply(reply):
    for k in ["type", "content", "why", "user_id"]:
        assert k in reply.keys()

    assert reply["type"] != "error"
    assert isinstance(reply["content"], str)
    assert "You did not configure" in reply["content"]

    # why
    why = reply["why"]
    assert {"input", "intermediate_steps", "memory", "model_interactions"} == set(why.keys())
    assert isinstance(why["input"], str)
    assert isinstance(why["intermediate_steps"], list)
    assert isinstance(why["memory"], dict)
    assert {"procedural", "declarative", "episodic"} == set(why["memory"].keys())
    assert isinstance(why["model_interactions"], list)
    
    # model interactions
    for mi in why["model_interactions"]:
        assert mi["model_type"] in ["llm", "embedder"]
        assert isinstance(mi["source"], str)
        assert isinstance(mi["prompt"], str)
        assert isinstance(mi["input_tokens"], int)
        assert mi["input_tokens"] > 0
        assert isinstance(mi["started_at"], float)
        assert time.time() - 1 < mi["started_at"] < time.time()

        if mi["model_type"] == "llm":
            assert isinstance(mi["reply"], str)
            assert "You did not configure" in mi["reply"]
            assert isinstance(mi["output_tokens"], int)
            assert mi["output_tokens"] > 0
            assert isinstance(mi["ended_at"], float)
            assert mi["ended_at"] > mi["started_at"]
        else:
            assert mi["model_type"] == "embedder"
            assert isinstance(mi["reply"], list)
            assert isinstance(mi["reply"][0], float)
            assert mi["source"] == "recall"
        


def test_websocket(client):
    # send websocket message
    res = send_websocket_message({"text": "It's late! It's late"}, client)

    check_correct_websocket_reply(res)


def test_websocket_multiple_messages(client):
    # send websocket message
    replies = send_n_websocket_messages(3, client)

    for res in replies:
        check_correct_websocket_reply(res)
