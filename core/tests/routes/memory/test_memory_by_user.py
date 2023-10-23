
from tests.utils import send_websocket_message

# episodic memories are saved having the correct user
def test_episodic_memory_by_user(client):

        # send websocket message from user A
        send_websocket_message({
            "text": "I am user A"
        }, client, user_id="A")

        # episodic recall (no user)
        params = {
            "text": "I am user"
        }
        response = client.get(f"/memory/recall/", params=params)
        json = response.json()
        assert response.status_code == 200
        episodic_memories = json["vectors"]["collections"]["episodic"]
        assert len(episodic_memories) == 0

        # episodic recall (memories from non existing user)
        params = {
            "text": "I am user",
            "user_id": "H"
        }
        response = client.get(f"/memory/recall/", params=params)
        json = response.json()
        assert response.status_code == 200
        episodic_memories = json["vectors"]["collections"]["episodic"]
        assert len(episodic_memories) == 0

        # episodic recall (memories from user A)
        params = {
            "text": "I am user",
            "user_id": "A"
        }
        response = client.get(f"/memory/recall/", params=params)
        json = response.json()
        assert response.status_code == 200
        episodic_memories = json["vectors"]["collections"]["episodic"]
        assert len(episodic_memories) == 1
        assert episodic_memories[0]["metadata"]["source"] == "A"

