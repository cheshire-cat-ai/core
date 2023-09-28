import os
import shutil

from typing import Any
from typing import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from tinydb import Query
from cat.db import models
from cat.db.database import Database
from cat.log import log

from cat.looking_glass.cheshire_cat import CheshireCat
from qdrant_client import QdrantClient
from cat.memory.vector_memory import VectorMemory

from cat.main import cheshire_cat_api


def clean_up_mocks():
    # clean up service files and mocks
    to_be_removed = [
        "cat/metadata-test.json", # legacy position, now moved into mocks folder
        "tests/mocks/metadata-test.json",
        "tests/mocks/mock_plugin.zip",
        "tests/mocks/mock_plugin_folder/mock_plugin",
        "tests/mocks/empty_folder"
    ]
    for tbr in to_be_removed:
        if os.path.exists(tbr):
            if os.path.isdir(tbr):
                shutil.rmtree(tbr)
            else:
                os.remove(tbr)
    
    # Uninstall mock plugin requirements
    os.system("pip uninstall -y pip-install-test")


@pytest.fixture(scope="function")
def app(monkeypatch) -> Generator[FastAPI, Any, None]:
    """
    Create a new setup on each test case, with new mocks for both Qdrant and TinyDB
    """

    # Use mock plugin folder
    def mock_plugin_folder(self, *args, **kwargs):
        return "tests/mocks/mock_plugin_folder/"
    monkeypatch.setattr(CheshireCat, "get_plugin_path", mock_plugin_folder)

    # Use in memory vector db
    def mock_connect_to_vector_memory(self, *args, **kwargs):
        self.vector_db = QdrantClient(":memory:")
    monkeypatch.setattr(VectorMemory, "connect_to_vector_memory", mock_connect_to_vector_memory)

    # Use a different json settings db
    def mock_get_file_name(self, *args, **kwargs):
        return "tests/mocks/metadata-test.json"
    monkeypatch.setattr(Database, "get_file_name", mock_get_file_name)

    # clean up service files and mocks
    clean_up_mocks()
    Database._instance = None
    
    _app = cheshire_cat_api
    yield _app
    
    
@pytest.fixture(scope="function")
def client(app: FastAPI, monkeypatch) -> Generator[TestClient, Any, None]:
    """
    Create a new FastAPI TestClient.
    """
    
    with TestClient(app) as client:
        yield client
