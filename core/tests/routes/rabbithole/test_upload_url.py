
from tests.utils import get_declarative_memory_contents

def test_rabbithole_upload_invalid_url(client):

    payload = {
        "url": "https://www.example.sbadabim"
    }
    response = client.post("/rabbithole/web/", json=payload)

    # check response
    assert response.status_code == 400
    json = response.json()
    assert json["detail"]["error"] == "Unable to reach the URL"
    
    # check declarative memory is still empty
    declarative_memories = get_declarative_memory_contents(client)
    assert len(declarative_memories) == 0


def test_rabbithole_upload_url(client):

    payload = {
        "url": "https://www.example.com"
    }
    response = client.post("/rabbithole/web/", json=payload)

    # check response
    assert response.status_code == 200
    json = response.json()
    assert json["info"] == "URL is being ingested asynchronously"
    assert json["url"] == payload["url"]

    # check declarative memories have been stored
    declarative_memories = get_declarative_memory_contents(client)
    assert len(declarative_memories) == 1
