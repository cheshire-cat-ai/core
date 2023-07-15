
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
def app() -> Generator[FastAPI, Any, None]:
    """
    Create a new setup on each test case.
    """
    
    # TODO: things to do before each testcase
    #Database._instance = None
    #Database.file_name = "metadata-test.json"
    Database().truncate()
    _app = cheshire_cat_api
    yield _app
    Database().truncate()
    # TODO: things to do after each testcase

@pytest.fixture(scope="function")
def client(app: FastAPI, monkeypatch) -> Generator[TestClient, Any, None]:
    """
    Create a new FastAPI TestClient that mocks both Qdrant and TinyDB.
    """

    # Use in memory vector db
    def mock_connect_to_vector_memory(self, *args, **kwargs):
        self.vector_db = QdrantClient(":memory:")

    monkeypatch.setattr(VectorMemory, "connect_to_vector_memory",
                        mock_connect_to_vector_memory)
    
    monkeypatch.setattr(Database, "file_name", "metadata-test.json")

    with TestClient(app) as client:
        yield client
