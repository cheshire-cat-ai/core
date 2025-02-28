from elasticsearch import Elasticsearch, AuthenticationException, AuthorizationException

from cat.memory.constants import COLLECTION_NAMES
from cat.memory.elasticsearch.vector_memory_collection import VectorMemoryCollectionES
from cat.log import log
from cat.env import get_env
# from cat.utils import singleton


# @singleton REFACTOR: worth it to have this (or LongTermMemory) as singleton?
class VectorMemoryES:
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
        for collection_name in COLLECTION_NAMES:
            # Instantiate collection
            collection = VectorMemoryCollectionES(
                client=self.vector_db,
                collection_name=collection_name,
                embedder_name=embedder_name,
                embedder_size=embedder_size,
            )

            # Update dictionary containing all collections
            # Useful for cross-searching and to create/use collections from plugins
            self.collections[collection_name] = collection

    def connect_to_vector_memory(self) -> None:
        es_cloud_id = get_env("CCAT_ES_CLOUD_ID")
        es_api_key = get_env("CCAT_ES_API_KEY")

        try:
            if es_cloud_id and len(es_cloud_id) > 0:
                log.info(f"Connecting to Elastic Cloud: {es_cloud_id}")
                self.vector_db = Elasticsearch(cloud_id=es_cloud_id, api_key=es_api_key)
            else:
                host = get_env("CCAT_ES_HOST")
                port = get_env("CCAT_ES_PORT")
                log.info(f"Connecting to Elastic Host: {host}:{port}")
                self.vector_db = Elasticsearch([f"{host}:{port}"], api_key=es_api_key)
        except AuthenticationException as err:
                print(f"Authentication error {err=}, {type(err)=}")
        except AuthorizationException as err:
                print(f"Authorization error {err=}, {type(err)=}")
        log.info(f"Connection established")

    def delete_collection(self, collection_name: str):
        """Delete specific vector indexes"""
        
        return self.collections[collection_name].delete_collection()
    
    def get_collection(self, collection_name: str):
        """Get index info"""
        
        return self.collections[collection_name].get()
