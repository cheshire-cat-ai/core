import os
import sys
import uuid
import socket
from typing import Any, List, Iterable, Optional
import requests
from cat.utils import extract_domain_from_url, is_https

from qdrant_client import QdrantClient
from qdrant_client.qdrant_remote import QdrantRemote

from cat.memory.vector_memory_collection import VectorMemoryCollection
from cat.log import log
# from cat.utils import singleton


#@singleton REFACTOR: worth it to have this (or LongTermMemory) as singleton?
class VectorMemory:
    local_vector_db = None

    def __init__(
            self,
            embedder_name=None,
            embedder_size=None,
        ) -> None:

        # connects to Qdrant and creates self.vector_db attribute
        self.connect_to_vector_memory()

        # Create vector collections
        # - Episodic memory will contain user and eventually cat utterances
        # - Declarative memory will contain uploaded documents' content
        # - Procedural memory will contain tools and knowledge on how to do things
        self.collections = {}
        for collection_name in ["episodic", "declarative", "procedural"]:
            # Instantiate collection
            collection = VectorMemoryCollection(
                client=self.vector_db,
                collection_name=collection_name,
                embedder_name=embedder_name,
                embedder_size=embedder_size,
            )

            # Update dictionary containing all collections
            # Useful for cross-searching and to create/use collections from plugins
            self.collections[collection_name] = collection

            # Have the collection as an instance attribute
            # (i.e. do things like cat.memory.vectors.declarative.something())
            setattr(self, collection_name, collection)

    def connect_to_vector_memory(self) -> None:
        db_path = "cat/data/local_vector_memory/"
        qdrant_host = os.getenv("QDRANT_HOST", db_path)

        if len(qdrant_host) == 0 or qdrant_host == db_path:
            log.info(f"Qdrant path: {db_path}")
            # Qdrant local vector DB client

            # reconnect only if it's the first boot and not a reload
            if VectorMemory.local_vector_db is None:
                VectorMemory.local_vector_db = QdrantClient(path=db_path, force_disable_check_same_thread=True)

            self.vector_db = VectorMemory.local_vector_db
        else:
            qdrant_port = int(os.getenv("QDRANT_PORT", 6333))
            qdrant_https = is_https(qdrant_host)
            qdrant_host = extract_domain_from_url(qdrant_host)
            qdrant_api_key = os.getenv("QDRANT_API_KEY")

            try:
                s = socket.socket()
                s.connect((qdrant_host, qdrant_port))
            except Exception:
                log.error(f"QDrant does not respond to {qdrant_host}:{qdrant_port}")
                sys.exit()
            finally:
                s.close()

            # Qdrant vector DB client
            self.vector_db = QdrantClient(
                host=qdrant_host,
                port=qdrant_port,
                https=qdrant_https,
                api_key=qdrant_api_key
            )
