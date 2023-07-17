
from typing import Any
from typing import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from tinydb import Query
from cat.db import models
from cat.db.database import Database
from cat.log import log

from qdrant_client import QdrantClient
from cat.memory.vector_memory import VectorMemory

from cat.main import cheshire_cat_api

@pytest.fixture(scope="function")
def app(monkeypatch) -> Generator[FastAPI, Any, None]:
    """
    Create a new setup on each test case, with new mocks for both Qdrant and TinyDB
    """
    
    # Use in memory vector db
    def mock_connect_to_vector_memory(self, *args, **kwargs):
        self.vector_db = QdrantClient(":memory:")
    monkeypatch.setattr(VectorMemory, "connect_to_vector_memory", mock_connect_to_vector_memory)

    # Use a different json settings db
    def mock_get_file_name(self, *args, **kwargs):
        return "metadata-test.json"
    monkeypatch.setattr(Database, "get_file_name", mock_get_file_name)
    
    Database._instance = None
    _app = cheshire_cat_api
    yield _app
    Database._instance.db.truncate()
    
@pytest.fixture(scope="function")
def client(app: FastAPI, monkeypatch) -> Generator[TestClient, Any, None]:
    """
    Create a new FastAPI TestClient.
    """
    
    with TestClient(app) as client:
        yield client
