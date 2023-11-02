import time
from tests.utils import send_websocket_message

# TODO: should be tested also with concurrency!
def test_working_memory_update(client):

    convos = {
        # user_id: n_messages
        "White Rabbit": 2,
        "Alice": 3
    }

    # send websocket messages
    for user_id, n_messages in convos.items():
        for m in range(n_messages):
            time.sleep(0.1)
            res = send_websocket_message({
                "text": f"Mex n.{m} from {user_id}"
            }, client, user_id=user_id)

    # check working memories
    for user_id, n_messages in convos.items():
        response = client.get(f"/memory/conversation_history/", headers={"user_id": user_id})
        json = response.json()
        assert response.status_code == 200
        assert "history" in json
        assert len(json["history"]) == n_messages * 2 # mex and reply
        for m_idx, m in enumerate(json["history"]):
            assert "who" in m
            assert "message" in m
            if m_idx%2==0: # even message
                m_number_from_user = int(m_idx/2)
                assert m["who"] == "Human"
                assert m["message"] == f"Mex n.{m_number_from_user} from {user_id}"
            else:
                assert m["who"] == "AI"
