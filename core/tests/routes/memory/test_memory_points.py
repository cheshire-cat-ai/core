import pytest
from tests.utils import send_websocket_message, get_declarative_memory_contents
from tests.conftest import FAKE_TIMESTAMP
import time

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
def test_create_memory_point(client, patch_time_now, collection):

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
    expected_metadata = {"when":FAKE_TIMESTAMP,"source": "user", **metadata}
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


# utility function that validates a list of points against an expected points payload
def _check_points(points, expected_points_payload):
    # check length
    assert len(points) == len(expected_points_payload)
    # check all the points contains id and vector
    for point in points:
        assert "id" in point
        assert "vector" in point 
    
    # check points payload
    points_payloads = [p["payload"] for p in points]
    # sort the list and compare payload
    points_payloads.sort(key=lambda p:p["page_content"])
    expected_points_payload.sort(key=lambda p:p["page_content"])
    assert points_payloads == expected_points_payload


@pytest.mark.parametrize("collection", ["episodic", "declarative"])
def test_get_collection_points(client, patch_time_now, collection):
    # create 100 points
    n_points = 100
    new_points = [{"content": f"MIAO {i}!","metadata": {"custom_key": f"custom_key_{i}"}} for i in range(n_points) ]

    # Add points
    for req_json in new_points:
        res = client.post(
            f"/memory/collections/{collection}/points", json=req_json
        )
        assert res.status_code == 200

    # get all the points no limit, by default is 100
    res = client.get(
        f"/memory/collections/{collection}/points",
    )
    assert res.status_code == 200
    json = res.json()

    points = json["points"]
    offset = json["next_offset"]

    assert offset is None # the result should contains all the points so no offset

    expected_payloads = [
        {"page_content":p["content"],
         "metadata":{"when":FAKE_TIMESTAMP,"source": "user", **p["metadata"]}  
        } for p in new_points
    ]
    _check_points(points, expected_payloads)



@pytest.mark.parametrize("collection", ["episodic", "declarative"])
def test_get_collection_points_offset(client, patch_time_now, collection):
    # create 200 points
    n_points = 200
    new_points = [{"content": f"MIAO {i}!","metadata": {"custom_key": f"custom_key_{i}"}} for i in range(n_points) ]

    # Add points
    for req_json in new_points:
        res = client.post(
            f"/memory/collections/{collection}/points", json=req_json
        )
        assert res.status_code == 200

    # get all the points with limit 10
    limit = 10
    next_offset = ""
    all_points = []

    while True:
        res = client.get(
            f"/memory/collections/{collection}/points?limit={limit}&offset={next_offset}",
        )
        assert res.status_code == 200
        json = res.json()
        points = json["points"]
        next_offset = json["next_offset"]
        assert len(points) == limit

        for point in points:
            all_points.append(point)

        if next_offset is None: # break if no new data
            break
    
    # create the expected payloads for all the points
    expected_payloads = [
        {"page_content":p["content"],
         "metadata":{"when":FAKE_TIMESTAMP,"source": "user", **p["metadata"]}  
        } for p in new_points
    ]
    _check_points(all_points, expected_payloads)


def test_get_all_points(client,patch_time_now):

    # create 50 points for episodic
    new_points_episodic = [{"content": f"MIAO {i}!","metadata": {"custom_key": f"custom_key_{i}_episodic"}} for i in range(50) ]

    # create 100 points for declarative
    new_points_declarative = [{"content": f"MIAO {i}!","metadata": {"custom_key": f"custom_key_{i}_declarative"}} for i in range(100) ]

    for point in new_points_episodic:
        res = client.post(
            f"/memory/collections/episodic/points", json=point
        )
        assert res.status_code == 200

    for point in new_points_declarative:
        res = client.post(
            f"/memory/collections/declarative/points", json=point
        )
        assert res.status_code == 200

    # get the points from all the collection with default limit (100 points)
    res = client.get(
        f"/memory/collections/points",
    )
    assert res.status_code == 200
    json = res.json()

    assert "episodic" in json
    assert "declarative" in json

    #check episodic points
    episodic_points = json["episodic"]["points"]
    # create the expected payloads for all the points
    expected_episodic_payloads = [
        {"page_content":p["content"],
            "metadata":{"when":FAKE_TIMESTAMP,"source": "user", **p["metadata"]}  
        } for p in new_points_episodic
    ]
    _check_points(episodic_points, expected_episodic_payloads)

    # check declarative points
    declarative_points = json["declarative"]["points"]
    # create the expected payloads for all the points
    expected_declarative_payloads = [
        {"page_content":p["content"],
            "metadata":{"when":FAKE_TIMESTAMP,"source": "user", **p["metadata"]}  
        } for p in new_points_declarative
    ]
    _check_points(declarative_points, expected_declarative_payloads)


