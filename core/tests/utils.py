import shutil
from urllib.parse import urlencode


# utility function to communicate with the cat via websocket
def send_websocket_message(msg, client, user_id="user", query_params=None):
    url = f"/ws/{user_id}"
    if query_params:
        url += "?" + urlencode(query_params)

    with client.websocket_connect(url) as websocket:

        # send ws message
        websocket.send_json(msg)
        # get reply
        reply = websocket.receive_json()

    return reply


# utility to send n messages via chat
def send_n_websocket_messages(num_messages, client):
    responses = []

    with client.websocket_connect("/ws") as websocket:
        for m in range(num_messages):
            message = {"text": f"Red Queen {m}"}
            # sed ws message
            websocket.send_json(message)
            # get reply
            reply = websocket.receive_json()
            responses.append(reply)

    return responses


def key_in_json(key, json):
    return key in json.keys()


# create a plugin zip out of the mock plugin folder.
# - Used to test plugin upload.
# - zip can be created flat (plugin files in root dir) or nested (plugin files in zipped folder)
def create_mock_plugin_zip(flat: bool):
    if flat:
        root_dir = "tests/mocks/mock_plugin"
        base_dir = "./"
    else:
        root_dir = "tests/mocks/"
        base_dir = "mock_plugin"

    return shutil.make_archive(
        base_name="tests/mocks/mock_plugin",
        format="zip",
        root_dir=root_dir,
        base_dir=base_dir,
    )


# utility to retrieve embedded tools from endpoint
def get_procedural_memory_contents(client):
    params = {"text": "random"}
    response = client.get("/memory/recall/", params=params)
    json = response.json()
    return json["vectors"]["collections"]["procedural"]


# utility to retrieve declarative memory contents
def get_declarative_memory_contents(client):
    params = {"text": "Something"}
    response = client.get("/memory/recall/", params=params)
    assert response.status_code == 200
    json = response.json()
    declarative_memories = json["vectors"]["collections"]["declarative"]
    return declarative_memories


# utility to get collections and point count from `GET /memory/collections` in a simpler format
def get_collections_names_and_point_count(client):
    response = client.get("/memory/collections")
    json = response.json()
    assert response.status_code == 200
    collections_n_points = {c["name"]: c["vectors_count"] for c in json["collections"]}
    return collections_n_points


def create_new_user(client):
    new_user = {"username": "Alice", "password": "wandering_in_wonderland"}
    response = client.post("/users", json=new_user)
    assert response.status_code == 200
    return response.json()