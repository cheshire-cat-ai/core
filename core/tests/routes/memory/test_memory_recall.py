

def test_memory_recall(client):

    ##### search without query should throw error
    response = client.get(f"/memory/recall/")
    json = response.json()
    assert response.status_code == 422

    ##### search with query
    params = {
        "text": "alice"
    }
    response = client.get(f"/memory/recall/", params=params)
    json = response.json()
    assert response.status_code == 200
    # query was received and embedded
    assert json["query"]["text"] == params["text"]
    assert type(json["query"]["vector"]) == list
    assert type(json["query"]["vector"][0]) == float
    # results are grouped by collection
    assert len(json["vectors"]["collections"]) == 3
    assert {"episodic", "declarative", "procedural"} == set(json["vectors"]["collections"].keys())
    for collection in json["vectors"]["collections"].keys():
        assert type(json["vectors"]["collections"][collection]) == list

    ##### search with query and k
    # TODO: insert in memory more than k memories per collections
    params = {
        "k": 2,
        "text": "alice"
    }
    response = client.get(f"/memory/recall/", params=params)
    json = response.json()
    assert response.status_code == 200
    for collection in json["vectors"]["collections"].keys():
        assert len(json["vectors"]["collections"][collection]) <= params["k"]
