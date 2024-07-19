import pytest
from tests.utils import send_websocket_message, get_declarative_memory_contents


def test_point_deleted(client):
    # send websocket message
    res = send_websocket_message({"text": "Hello Mad Hatter"}, client)

    # get point back
    params = {"text": "Mad Hatter"}
    response = client.get("/memory/recall/", params=params)
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
    res = client.delete("/memory/collections/episodic/points/wrong_id")
    assert res.status_code == 400
    assert res.json()["detail"]["error"] == "Point does not exist."

    # delete point (all right)
    res = client.delete(f"/memory/collections/episodic/points/{memory['id']}")
    assert res.status_code == 200
    assert res.json()["deleted"] == memory["id"]

    # there is no point now
    params = {"text": "Mad Hatter"}
    response = client.get("/memory/recall/", params=params)
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
    with open(file_path, "rb") as f:
        files = {"file": (file_name, f, content_type)}

        response = client.post("/rabbithole/", files=files)
    # check response
    assert response.status_code == 200
    # check memory contents
    declarative_memories = get_declarative_memory_contents(client)
    assert len(declarative_memories) == expected_chunks

    # upload another document
    with open(file_path, "rb") as f:
        files = {"file": ("sample2.pdf", f, content_type)}

        response = client.post("/rabbithole/", files=files)
    # check response
    assert response.status_code == 200
    # check memory contents
    declarative_memories = get_declarative_memory_contents(client)
    assert len(declarative_memories) == expected_chunks * 2

    # delete nothing
    metadata = {"source": "invented.pdf"}
    res = client.request(
        "DELETE", "/memory/collections/declarative/points", json=metadata
    )
    # check memory contents
    assert res.status_code == 200
    declarative_memories = get_declarative_memory_contents(client)
    assert len(declarative_memories) == expected_chunks * 2

    # delete first document
    metadata = {"source": "sample.pdf"}
    res = client.request(
        "DELETE", "/memory/collections/declarative/points", json=metadata
    )
    # check memory contents
    assert res.status_code == 200
    json = res.json()
    assert isinstance(json["deleted"], list)
    # assert len(json["deleted"]) == expected_chunks
    declarative_memories = get_declarative_memory_contents(client)
    assert len(declarative_memories) == expected_chunks

    # delete second document
    metadata = {"source": "sample2.pdf"}
    res = client.request(
        "DELETE", "/memory/collections/declarative/points", json=metadata
    )
    # check memory contents
    assert res.status_code == 200
    declarative_memories = get_declarative_memory_contents(client)
    assert len(declarative_memories) == 0


def create_point_wrong_collection(client):

    req_json = {
        "content": "Hello dear"
    }

    # wrong collection
    res = client.post(
        "/memory/collections/wrongcollection/points", json=req_json
    )
    assert res.status_code == 400
    assert "Collection does not exist" in res.json()["detail"]["error"]

    # cannot write procedural point
    res = client.post(
        "/memory/collections/procedural/points", json=req_json
    )
    assert res.status_code == 400
    assert "Procedural memory is read-only" in res.json()["detail"]["error"]


@pytest.mark.parametrize("collection", ["episodic", "declarative"])
def test_create_memory_point(client, collection):

    # create a point
    content = "Hello dear"
    metadata = {"custom_key": "custom_value"}
    req_json = {
        "content": content,
        "metadata": metadata,
    }
    res = client.post(
        f"/memory/collections/{collection}/points", json=req_json
    )
    assert res.status_code == 200
    json = res.json()
    assert json["content"] == content
    expected_metadata = {"source": "user", **metadata}
    assert json["metadata"] == expected_metadata
    assert "id" in json
    assert "vector" in json
    assert isinstance(json["vector"], list)
    assert isinstance(json["vector"][0], float)

    # check memory contents
    params = {"text": "dear, hello"}
    response = client.get("/memory/recall/", params=params)
    json = response.json()
    assert response.status_code == 200
    assert len(json["vectors"]["collections"][collection]) == 1
    memory = json["vectors"]["collections"][collection][0]
    assert memory["page_content"] == content
    assert memory["metadata"] == expected_metadata


