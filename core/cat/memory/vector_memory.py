import sys
import socket
from cat.utils import extract_domain_from_url, is_https

from qdrant_client import QdrantClient

from cat.memory.vector_memory_collection import VectorMemoryCollection
from cat.log import log
from cat.env import get_env
# from cat.utils import singleton


# @singleton REFACTOR: worth it to have this (or LongTermMemory) as singleton?
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
        qdrant_host = get_env("CCAT_QDRANT_HOST")

        if not qdrant_host:
            log.debug(f"Qdrant path: {db_path}")
            # Qdrant local vector DB client

            # reconnect only if it's the first boot and not a reload
            if VectorMemory.local_vector_db is None:
                VectorMemory.local_vector_db = QdrantClient(
                    path=db_path, force_disable_check_same_thread=True
                )

            self.vector_db = VectorMemory.local_vector_db
        else:
            # Qdrant remote or in other container
            qdrant_port = int(get_env("CCAT_QDRANT_PORT"))
            qdrant_https = is_https(qdrant_host)
            qdrant_host = extract_domain_from_url(qdrant_host)
            qdrant_api_key = get_env("CCAT_QDRANT_API_KEY")

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
                api_key=qdrant_api_key,
            )

    def delete_collection(self, collection_name: str):
        """Delete specific vector collection"""
        
        return self.vector_db.delete_collection(collection_name)
    
    def get_collection(self, collection_name: str):
        """Get collection info"""
        
        return self.vector_db.get_collection(collection_name)
