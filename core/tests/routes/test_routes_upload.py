import time
import random
import json
import uuid


def test_upload_memory(client):
    fake_memory = {
        "embedder": "OpenAIEmbeddings",
        "collections": {
            "declarative": [{
                "page_content": "test_memory",
                "metadata": {
                    "source": "user",
                    "when": time.time()
                },
                "id": str(uuid.uuid4()),
                "vector": [random.random() for _ in range(1536)]
            }]
        }
    }

    response = client.post("/rabbithole/memory/",
                           files={
                               "file": ("test_file.json",
                                        json.dumps(fake_memory))
                           },
                           headers={"accept": "application/json"})

    assert response.status_code == 200
