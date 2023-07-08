
# utility to retrieve declarative memory contents
def get_declarative_memory_contents(client):
    params = {
        "text": "Something"
    }
    response = client.get(f"/memory/recall/", params=params)
    assert response.status_code == 200
    json = response.json()
    declarative_memories = json["vectors"]["collections"]["declarative"]
    return declarative_memories


def test_rabbithole_upload_txt(client):

    # check declarative memory is empty
    declarative_memories = get_declarative_memory_contents(client)
    assert len(declarative_memories) == 0

    content_type = "text/plain"
    file_name = "sample.txt"
    file_path = f"tests/mocks/{file_name}"
    with open(file_path, 'rb') as f:
        files = {
            'file': (file_name, f, content_type)
        }

        response = client.post("/rabbithole/", files=files)

    # check response
    assert response.status_code == 200
    json = response.json()
    assert json["filename"] == file_name
    assert json["content-type"] == content_type
    assert "File is being ingested" in json["info"]

    # check memory contents
    # check declarative memory is empty
    declarative_memories = get_declarative_memory_contents(client)
    assert len(declarative_memories) == 21


def test_rabbithole_upload_pdf(client):

    # check declarative memory is empty
    declarative_memories = get_declarative_memory_contents(client)
    assert len(declarative_memories) == 0

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
    json = response.json()
    assert json["filename"] == file_name
    assert json["content-type"] == content_type
    assert "File is being ingested" in json["info"]

    # check memory contents
    # check declarative memory is empty
    declarative_memories = get_declarative_memory_contents(client)
    assert len(declarative_memories) == 20