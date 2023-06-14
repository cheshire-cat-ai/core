import os
import sys
import socket
import time
from typing import Any, Callable

from cat.log import log
from qdrant_client import QdrantClient
from langchain.vectorstores import Qdrant
from langchain.docstore.document import Document
from qdrant_client.http.models import (Distance, VectorParams,  SearchParams,
ScalarQuantization, ScalarQuantizationConfig, ScalarType, QuantizationSearchParams)

# TODO: hook get_embedder_size and remove dict


class VectorMemory:
    def __init__(self, cat, verbose=False) -> None:
        self.verbose = verbose

        # Get embedder from Cat instance
        self.embedder = cat.embedder

        if self.embedder is None:
            raise Exception("No embedder passed to VectorMemory")

        qdrant_host = os.getenv("VECTOR_MEMORY_HOST", "cheshire_cat_vector_memory")
        qdrant_port = int(os.getenv("VECTOR_MEMORY_PORT", 6333))

        try:
            s = socket.socket()
            s.connect((qdrant_host, qdrant_port))
        except Exception:
            log("QDrant does not respond to %s:%s" % (qdrant_host, qdrant_port), "ERROR")
            sys.exit()
        finally:
            s.close()

        # Qdrant vector DB client
        self.vector_db = QdrantClient(
            host=qdrant_host,
            port=qdrant_port,
        )

        # Episodic memory will contain user and eventually cat utterances
        self.episodic = VectorMemoryCollection(
            cat=cat,
            client=self.vector_db,
            collection_name="episodic",
            embedding_function=self.embedder.embed_query,
        )

        # Declarative memory will contain uploaded documents' content (and summaries)
        self.declarative = VectorMemoryCollection(
            cat=cat,
            client=self.vector_db,
            collection_name="declarative",
            embedding_function=self.embedder.embed_query,
        )

        # Procedural memory will contain tools and knowledge on how to do things
        self.procedural = VectorMemoryCollection(
            cat=cat,
            client=self.vector_db,
            collection_name="procedural",
            embedding_function=self.embedder.embed_query,
        )

        # Dictionary containing all collections
        # Useful for cross-searching and to create/use collections from plugins
        self.collections = {
            "episodic": self.episodic,
            "declarative": self.declarative,
            "procedural": self.procedural,
        }


class VectorMemoryCollection(Qdrant):
    def __init__(self, cat, client: Any, collection_name: str, embedding_function: Callable):
        super().__init__(client, collection_name, embedding_function)

        # Get a Cat instance
        self.cat = cat

        # Check if memory collection exists, otherwise create it and add first memory
        self.create_collection_if_not_exists()

    def create_collection_if_not_exists(self):
        # create collection if it does not exist
        try:
            self.client.get_collection(self.collection_name)
            tabula_rasa = False
            log(f'Collection "{self.collection_name}" already present in vector store', "INFO")
        except:
            log(f"Creating collection {self.collection_name} ...", "INFO")
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
                quantization_config=ScalarQuantization(
                        scalar=ScalarQuantizationConfig(
                            type=ScalarType.INT8,
                            quantile=0.99,
                            always_ram=False
                        )
                    )
                # TODO: if we change the embedder, how do we know the dimensionality?
            )
            tabula_rasa = True

        # TODO: if the embedder changed, a new vectorstore must be created
        # TODO: need a more elegant solution
        if tabula_rasa:
            # Hard coded overridable first memory saved in both collections
            first_memory = Document(
                page_content="I am the Cheshire Cat", metadata={"source": "cheshire-cat", "when": time.time()}
            )

            # Execute hook to override the first inserted memory
            first_memory = self.cat.mad_hatter.execute_hook("before_collection_created", first_memory)

            # insert first point in the collection
            self.add_texts(
                [first_memory.page_content],
                [first_memory.metadata],
            )

        log(dict(self.client.get_collection(self.collection_name)), "DEBUG")

    # retrieve similar memories from text
    def recall_memories_from_text(self, text, metadata=None, k=3):
        # embed the text
        query_embedding = self.embedding_function(text)

        # search nearest vectors
        return self.recall_memories_from_embedding(query_embedding, metadata=metadata, k=k)

    # retrieve similar memories from embedding
    def recall_memories_from_embedding(self, embedding, metadata=None, k=3):
        # retrieve memories
        memories = self.client.search(
            collection_name=self.collection_name,
            query_vector=embedding,
            query_filter=self._qdrant_filter_from_dict(metadata),
            with_payload=True,
            with_vectors=True,
            limit=k,
            search_params=SearchParams(
                quantization=QuantizationSearchParams(
                    ignore=False,
                    rescore=True
                )
            )
        )
        return [
            (
                self._document_from_scored_point(m, self.content_payload_key, self.metadata_payload_key),
                m.score,
                m.vector
            )
            for m in memories
        ]
