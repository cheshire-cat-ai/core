from tests.utils import send_websocket_message


# episodic memories are saved having the correct user
def test_episodic_memory_by_user(client):
    # send websocket message from user C
    send_websocket_message(
        {
            "text": "I am user C",
        },
        client,
        user_id="C",
    )

    # episodic recall (no user)
    params = {"text": "I am user"}
    response = client.get("/memory/recall/", params=params)
    json = response.json()
    assert response.status_code == 200
    episodic_memories = json["vectors"]["collections"]["episodic"]
    assert len(episodic_memories) == 0

    # episodic recall (memories from non existing user)
    params = {"text": "I am user not existing"}
    response = client.get(
        "/memory/recall/", params=params, headers={"user_id": "not_existing"}
    )
    json = response.json()
    assert response.status_code == 200
    episodic_memories = json["vectors"]["collections"]["episodic"]
    assert len(episodic_memories) == 0

    # episodic recall (memories from user C)
    params = {"text": "I am user C"}
    response = client.get("/memory/recall/", params=params, headers={"user_id": "C"})
    json = response.json()
    assert response.status_code == 200
    episodic_memories = json["vectors"]["collections"]["episodic"]
    assert len(episodic_memories) == 1
    assert episodic_memories[0]["metadata"]["source"] == "C"
