from tests.utils import send_websocket_message, get_declarative_memory_contents


def test_point_deleted(client):

    # send websocket message
    res = send_websocket_message({
        "text": "Hello Mad Hatter"
    }, client)

    # get point back
    params = {
        "text": "Mad Hatter"
    }
    response = client.get(f"/memory/recall/", params=params)
    json = response.json()
    assert response.status_code == 200
    assert len(json["vectors"]["collections"]["episodic"]) == 1
    memory = json["vectors"]["collections"]["episodic"][0]
    assert memory["page_content"] == "Hello Mad Hatter"

    # delete point (wrong collection)
    res = client.delete(f"/memory/collections/wrongcollection/points/{memory['id']}")
    assert res.status_code == 400
    assert res.json()["detail"]["error"] == "Collection does not exist."

    # delete point (wrong id)
    res = client.delete(f"/memory/collections/episodic/points/wrong_id")
    assert res.status_code == 400
    assert res.json()["detail"]["error"] == "Point does not exist."

    # delete point (all right)
    res = client.delete(f"/memory/collections/episodic/points/{memory['id']}")
    assert res.status_code == 200
    assert res.json()["deleted"] == memory['id']

    # there is no point now
    params = {
        "text": "Mad Hatter"
    }
    response = client.get(f"/memory/recall/", params=params)
    json = response.json()
    assert response.status_code == 200
    assert len(json["vectors"]["collections"]["episodic"]) == 0

    # delete again the same point (should not be found)
    res = client.delete(f"/memory/collections/episodic/points/{memory['id']}")
    assert res.status_code == 400
    assert res.json()["detail"]["error"] == "Point does not exist."


# test delete points by filter
# TODO: have a fixture uploading docs and separate test cases
def test_points_deleted_by_metadata(client):

    expected_chunks = 4 

    # upload to rabbithole a document
    content_type = "application/pdf"
    file_name = "sample.pdf"
    file_path = f"tests/mocks/{file_name}"
    with open(file_path, 'rb') as f:
        files = {
            'file': (file_name, f, content_type)
        }

        response = client.post("/rabbithole/", files=files)
    # check response
    assert response.status_code == 200
    # check memory contents
    declarative_memories = get_declarative_memory_contents(client)
    assert len(declarative_memories) == expected_chunks

    # upload another document
    with open(file_path, 'rb') as f:
        files = {
            'file': ("sample2.pdf", f, content_type)
        }

        response = client.post("/rabbithole/", files=files)
    # check response
    assert response.status_code == 200
    # check memory contents
    declarative_memories = get_declarative_memory_contents(client)
    assert len(declarative_memories) == expected_chunks * 2

    # delete nothing
    metadata = {
        "source": "invented.pdf"
    }
    res = client.request("DELETE", "/memory/collections/declarative/points", json=metadata)
    # check memory contents
    assert res.status_code == 200
    declarative_memories = get_declarative_memory_contents(client)
    assert len(declarative_memories) == expected_chunks * 2

    # delete first document
    metadata = {
        "source": "sample.pdf"
    }
    res = client.request("DELETE", "/memory/collections/declarative/points", json=metadata)
    # check memory contents
    assert res.status_code == 200
    json = res.json()
    assert type(json["deleted"]) == list
    #assert len(json["deleted"]) == expected_chunks
    declarative_memories = get_declarative_memory_contents(client)
    assert len(declarative_memories) == expected_chunks

    # delete second document
    metadata = {
        "source": "sample2.pdf"
    }
    res = client.request("DELETE", "/memory/collections/declarative/points", json=metadata)
    # check memory contents
    assert res.status_code == 200
    declarative_memories = get_declarative_memory_contents(client)
    assert len(declarative_memories) == 0
