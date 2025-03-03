import os

from cat.memory.elasticsearch.vector_memory import VectorMemoryES
from cat.memory.qdrant.vector_memory import VectorMemoryQdrant

from cat.log import log

from cat.memory.constants import COLLECTION_NAMES
from cat.memory.collection_info import CollectionInfo
# from cat.utils import singleton


#@singleton REFACTOR: worth it to have this (or LongTermMemory) as singleton?
class VectorMemory:


    def __init__(
            self,
            vector_memory_config={}
        ) -> None:

        host_type = os.getenv("HOST_TYPE", "qdrant")
        log.info(host_type)
        if len(host_type) == 0 or host_type == "qdrant":
            self.vector_db = VectorMemoryQdrant(**vector_memory_config)
        else:
            self.vector_db = VectorMemoryES(**vector_memory_config)

        # Create vector collections
        # - Episodic memory will contain user and eventually cat utterances
        # - Declarative memory will contain uploaded documents' content
        # - Procedural memory will contain tools and knowledge on how to do things
        self.collections = self.vector_db.collections
        for collection_name in COLLECTION_NAMES:
            log.info(collection_name)

            # Have the collection as an instance attribute
            # (i.e. do things like cat.memory.vectors.declarative.something())
            setattr(self, collection_name, self.vector_db.collections[collection_name])

    def connect_to_vector_memory(self) -> None:
        """Ask the specific vector_db to connect"""

        self.vector_db.connect_to_vector_memory()

    def delete_collection(self, collection_name: str):
        """Delete specific vector collection"""
        
        return self.vector_db.delete_collection(collection_name)
    
    def get_collection(self, collection_name: str) -> CollectionInfo:
        """Get collection info"""
        
        return self.vector_db.get_collection(collection_name)
