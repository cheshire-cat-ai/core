import os
import time
from dataclasses import dataclass

from cat.utils import log
from qdrant_client import QdrantClient
from langchain.vectorstores import Qdrant
from qdrant_client.http.models import Distance, VectorParams


@dataclass
class VectorMemoryConfig:
    host: str = os.getenv("VECTOR_MEMORY_HOST", "vector-memory")
    port: int = int(os.getenv("VECTOR_MEMORY_PORT", 6333))


class VectorStore:
    def __init__(self, vm_config: VectorMemoryConfig) -> None:
        self.client = QdrantClient(host=vm_config.host, port=vm_config.port)

    def get_vector_store(self, collection_name, embedder):
        # create collection if it does not exist
        try:
            self.client.get_collection(collection_name)
            tabula_rasa = False
            log(f'Collection "{collection_name}" already present in vector store')
        except:
            log(f"Creating collection {collection_name} ...")
            self.client.recreate_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
                # TODO: if we change the embedder, how do we know the dimensionality?
            )
            tabula_rasa = True

        vector_memory = Qdrant(
            self.client, collection_name, embedding_function=embedder.embed_query
        )

        if tabula_rasa:
            vector_memory.add_texts(
                ["I am the Cheshire Cat"],
                [
                    {
                        "who": "cheshire-cat",
                        "when": time.time(),
                        "text": "I am the Cheshire Cat",
                    }
                ],
            )

        log(dict(self.client.get_collection(collection_name)))

        return vector_memory
