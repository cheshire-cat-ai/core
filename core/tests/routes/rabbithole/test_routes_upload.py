import json
import time
import uuid
import random
import pytest
from fastapi import HTTPException


def test_upload_memory(client):
    
    # Read fake memory
    memory_path = "tests/mocks/sample.json"
    with open(memory_path, "r") as f:
        fake_memory = json.load(f)

    response = client.post(
        "/rabbithole/memory/",
        files={
            "file": ("sample.json", fake_memory)
        },
        #headers={"accept": "application/json"}
    )

    assert response.status_code == 200


async def test_embedder_check(client):
    # Create fake memory
    fake_memory = {
        "embedder": "FakeEmbedder",
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

    with pytest.raises(HTTPException) as e:
        # Get response
        _ = await client.post("/rabbithole/memory/",
                              files={
                                  "file": ("test_file.json",
                                           json.dumps(fake_memory))
                              },
                              headers={"accept": "application/json"})

    assert isinstance(e.value, HTTPException)
    assert e.value.status_code == 422
    assert e.value.detail == "Embedding size mismatch: vectors length should be 1536"


def test_embedder_size(client):
    # Create fake memory
    fake_memory = {
        "embedder": "FakeEmbedder",
        "collections": {
            "declarative": [{
                "page_content": "test_memory",
                "metadata": {
                    "source": "user",
                    "when": time.time()
                },
                "id": str(uuid.uuid4()),
                "vector": [random.random() for _ in range(15)]
            }]
        }
    }

    with pytest.raises(HTTPException) as e:
        # Get response
        _ = client.post("/rabbithole/memory/",
                        files={
                            "file": ("test_file.json",
                                     json.dumps(fake_memory))
                        },
                        headers={"accept": "application/json"})
