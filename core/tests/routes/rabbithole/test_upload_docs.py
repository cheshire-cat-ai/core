
from tests.utils import get_declarative_memory_contents


def test_rabbithole_upload_txt(client):

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
    assert json["content_type"] == content_type
    assert "File is being ingested" in json["info"]

    # check memory contents
    # check declarative memory is empty
    declarative_memories = get_declarative_memory_contents(client)
    assert len(declarative_memories) == 2


def test_rabbithole_upload_pdf(client):

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
    assert json["content_type"] == content_type
    assert "File is being ingested" in json["info"]

    # check memory contents
    # check declarative memory is empty
    declarative_memories = get_declarative_memory_contents(client)
    assert len(declarative_memories) == 2