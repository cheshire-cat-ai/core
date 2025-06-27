from tests.utils import send_n_websocket_messages


# search on default startup memory
def test_memory_recall_default_success(client):
    params = {"text": "Red Queen"}
    response = client.post("/memory/recall/", json=params)
    json = response.json()
    assert response.status_code == 200

    # query was received and embedded
    assert json["query"]["text"] == params["text"]
    assert isinstance(json["query"]["vector"], list)
    assert isinstance(json["query"]["vector"][0], float)

    # results are grouped by collection
    assert len(json["vectors"]["collections"]) == 3
    assert {"episodic", "declarative", "procedural"} == set(
        json["vectors"]["collections"].keys()
    )

    # initial collections contents
    for collection in json["vectors"]["collections"].keys():
        assert isinstance(json["vectors"]["collections"][collection], list)
        if collection == "procedural":
            assert len(json["vectors"]["collections"][collection]) > 0
        else:
            assert len(json["vectors"]["collections"][collection]) == 0


# search without query should throw error
def test_memory_recall_without_query_error(client):
    response = client.post("/memory/recall")
    assert response.status_code == 400


# search with query
def test_memory_recall_success(client):
    # send a few messages via chat
    num_messages = 3
    send_n_websocket_messages(num_messages, client)

    # recall
    params = {"text": "Red Queen"}
    response = client.post("/memory/recall/", json=params)
    json = response.json()
    assert response.status_code == 200
    episodic_memories = json["vectors"]["collections"]["episodic"]
    assert len(episodic_memories) == num_messages  # all 3 retrieved


# search with query and k
def test_memory_recall_with_k_success(client):
    # send a few messages via chat
    num_messages = 6
    send_n_websocket_messages(num_messages, client)

    # recall at max k memories
    max_k = 2
    params = {"k": max_k, "text": "Red Queen"}
    response = client.post("/memory/recall/", json=params)
    json = response.json()
    assert response.status_code == 200
    episodic_memories = json["vectors"]["collections"]["episodic"]
    assert len(episodic_memories) == max_k  # only 2 of 6 memories recalled

# search with query and metadata
def test_memory_recall_with_metadata(client):
    messages = [
        {
            "content": "MIAO_1",
            "metadata": {"key_1":"v1","key_2":"v2"},
        },
        {
            "content": "MIAO_2",
            "metadata": {"key_1":"v1","key_2":"v3"},
        },
        {
            "content": "MIAO_3",
            "metadata": {},
        }
    ]

    # insert a new points with metadata
    for req_json in messages:
        client.post(
            "/memory/collections/episodic/points", json=req_json
        )

    # recall with metadata
    params = {"text": "MIAO", "metadata":{"key_1":"v1"}}
    response = client.post("/memory/recall/", json=params)
    json = response.json()
    assert response.status_code == 200
    episodic_memories = json["vectors"]["collections"]["episodic"]
    assert len(episodic_memories) == 2

    # recall with metadata multiple keys in metadata
    params = {"text": "MIAO", "metadata":{"key_1":"v1","key_2":"v2"}}
    response = client.post("/memory/recall/", json=params)
    json = response.json()
    assert response.status_code == 200
    episodic_memories = json["vectors"]["collections"]["episodic"]
    assert len(episodic_memories) == 1
    assert episodic_memories[0]["page_content"] == "MIAO_1"



