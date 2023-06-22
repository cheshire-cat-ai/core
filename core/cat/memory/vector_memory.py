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

        # get current embedding size (langchain classes do not store it)
        self.embedder_size = len(cat.embedder.embed_query("hello world"))

        # Create vector collections
        # - Episodic memory will contain user and eventually cat utterances
        # - Declarative memory will contain uploaded documents' content (and summaries)
        # - Procedural memory will contain tools and knowledge on how to do things
        self.collections = {}
        for collection_name in ["episodic", "declarative", "procedural"]:

            # Instantiate collection
            collection = VectorMemoryCollection(
                cat=cat,
                client=self.vector_db,
                collection_name=collection_name,
                embedding_function=self.embedder.embed_query,
                vector_size = self.embedder_size,
            )

            # Update dictionary containing all collections
            # Useful for cross-searching and to create/use collections from plugins
            self.collections[collection_name] = collection
            
            # Have the collection as an instance attribute
            # (i.e. do things like cat.memory.vectors.declarative.something())
            setattr(self, collection_name, collection)


class VectorMemoryCollection(Qdrant):

    def __init__(self, cat, client: Any, collection_name: str, embedding_function: Callable, vector_size: int):

        super().__init__(client, collection_name, embedding_function)

        # Get a Cat instance
        self.cat = cat
        
        # Set embedding size (may be changed at runtime)
        self.embedder_size = vector_size

        # Check if memory collection exists, otherwise create it
        self.create_collection_if_not_exists()

    def create_collection_if_not_exists(self):
        # create collection if it does not exist
        try:
            self.client.get_collection(self.collection_name)
            log(f'Collection "{self.collection_name}" already present in vector store', "INFO")
            if self.client.get_collection(self.collection_name).config.params.vectors.size==self.embedder_size:
                log(f'Collection "{self.collection_name}" has the same size of the embedder', "INFO")
            else:
                log(f'Collection "{self.collection_name}" has different size of the embedder', "WARNING")
                # TODO: dump collection on disk before deleting, so it can be recovered
                self.client.delete_collection(self.collection_name)
                log(f'Collection "{self.collection_name}" deleted', "WARNING")
                self.create_collection()
        except:
            self.create_collection()

        log(f"Collection {self.collection_name}:", "INFO")
        log(dict(self.client.get_collection(self.collection_name)), "INFO")

    # create collection
    def create_collection(self):

        self.cat.mad_hatter.execute_hook('before_collection_created', self)
        
        log(f"Creating collection {self.collection_name} ...", "WARNING")
        self.client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=self.embedder_size, distance=Distance.COSINE),
            quantization_config=ScalarQuantization(
                scalar=ScalarQuantizationConfig(
                    type=ScalarType.INT8,
                    quantile=0.99,
                    always_ram=False
                )
            )
        )

        self.cat.mad_hatter.execute_hook('after_collection_created', self)

    # retrieve similar memories from text
    def recall_memories_from_text(self, text, metadata=None, k=5, threshold=0.0):
        # embed the text
        query_embedding = self.embedding_function(text)

        # search nearest vectors
        return self.recall_memories_from_embedding(
            query_embedding, metadata=metadata, k=k, threshold=threshold
        )

    # retrieve similar memories from embedding
    def recall_memories_from_embedding(self, embedding, metadata=None, k=5, threshold=0.0):
        # retrieve memories
        memories = self.client.search(
            collection_name=self.collection_name,
            query_vector=embedding,
            query_filter=self._qdrant_filter_from_dict(metadata),
            with_payload=True,
            with_vectors=True,
            limit=k,
            score_threshold=threshold,
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
