import os
import sys
import socket
from typing import Any
import requests

from cat.log import log
from qdrant_client import QdrantClient
from qdrant_client.qdrant_remote import QdrantRemote
from langchain.embeddings.base import Embeddings
from langchain.vectorstores import Qdrant
from qdrant_client.http.models import (
    Distance,
    VectorParams,
    SearchParams,
    ScalarQuantization,
    ScalarQuantizationConfig,
    ScalarType,
    QuantizationSearchParams,
    CreateAliasOperation,
    CreateAlias,
    OptimizersConfigDiff,
)


class VectorMemory:
    local_vector_db = None

    def __init__(self, cat, verbose=False) -> None:
        self.verbose = verbose

        # Get embedder from Cat instance
        self.embedder = cat.embedder

        if self.embedder is None:
            raise Exception("No embedder passed to VectorMemory")

        self.connect_to_vector_memory()

        # get current embedding size (langchain classes do not store it)
        # TODO: move the embedder size in create collection
        self.embedder_size = len(cat.embedder.embed_query("hello world"))

        # Create vector collections
        # - Episodic memory will contain user and eventually cat utterances
        # - Declarative memory will contain uploaded documents' content
        # - Procedural memory will contain tools and knowledge on how to do things
        self.collections = {}
        for collection_name in ["episodic", "declarative", "procedural"]:
            # Instantiate collection
            collection = VectorMemoryCollection(
                cat=cat,
                client=self.vector_db,
                collection_name=collection_name,
                embeddings=self.embedder,
                vector_size=self.embedder_size,
            )

            # Update dictionary containing all collections
            # Useful for cross-searching and to create/use collections from plugins
            self.collections[collection_name] = collection

            # Have the collection as an instance attribute
            # (i.e. do things like cat.memory.vectors.declarative.something())
            setattr(self, collection_name, collection)

    def connect_to_vector_memory(self) -> None:
        db_path = "local_vector_memory/"
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
            )


class VectorMemoryCollection(Qdrant):
    def __init__(
        self,
        cat,
        client: Any,
        collection_name: str,
        embeddings: Embeddings,
        vector_size: int,
    ):
        super().__init__(client, collection_name, embeddings)

        # Get a Cat instance
        self.cat = cat

        # Set embedder name for aliases
        if hasattr(self.cat.embedder, "model"):
            self.embedder_name = self.cat.embedder.model
        elif hasattr(self.cat.embedder, "repo_id"):
            self.embedder_name = self.cat.embedder.repo_id
        else:
            self.embedder_name = "default_embedder"

        # Set embedding size (may be changed at runtime)
        self.embedder_size = vector_size

        # Check if memory collection exists also in vectorDB, otherwise create it
        self.create_db_collection_if_not_exists()

        # Check db collection vector size is same as embedder size
        self.check_embedding_size()

        # log collection info
        log.info(f"Collection {self.collection_name}:")
        log.info(dict(self.client.get_collection(self.collection_name)))

    def check_embedding_size(self):
        # having the same size does not necessarily imply being the same embedder
        # having vectors with the same size but from diffent embedder in the same vector space is wrong
        same_size = (
            self.client.get_collection(self.collection_name).config.params.vectors.size
            == self.embedder_size
        )
        alias = self.embedder_name + "_" + self.collection_name
        if (
            alias
            == self.client.get_collection_aliases(self.collection_name)
            .aliases[0]
            .alias_name
            and same_size
        ):
            log.info(f'Collection "{self.collection_name}" has the same embedder')
        else:
            log.warning(f'Collection "{self.collection_name}" has different embedder')
            # Memory snapshot saving can be turned off in the .env file with:
            # SAVE_MEMORY_SNAPSHOTS=false
            if os.getenv("SAVE_MEMORY_SNAPSHOTS") == "true":
                # dump collection on disk before deleting
                self.save_dump()
                log.info(f'Dump "{self.collection_name}" completed')

            self.client.delete_collection(self.collection_name)
            log.warning(f'Collection "{self.collection_name}" deleted')
            self.create_collection()

    def create_db_collection_if_not_exists(self):
        # is collection present in DB?
        collections_response = self.client.get_collections()
        for c in collections_response.collections:
            if c.name == self.collection_name:
                # collection exists. Do nothing
                log.info(
                    f'Collection "{self.collection_name}" already present in vector store'
                )
                return

        self.create_collection()

    # create collection
    def create_collection(self):
        log.warning(f"Creating collection {self.collection_name} ...")
        self.client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.embedder_size, distance=Distance.COSINE
            ),
            # hybrid mode: original vector on Disk, quantized vector in RAM
            optimizers_config=OptimizersConfigDiff(memmap_threshold=20000),
            quantization_config=ScalarQuantization(
                scalar=ScalarQuantizationConfig(
                    type=ScalarType.INT8, quantile=0.95, always_ram=True
                )
            ),
            # shard_number=3,
        )

        self.client.update_collection_aliases(
            change_aliases_operations=[
                CreateAliasOperation(
                    create_alias=CreateAlias(
                        collection_name=self.collection_name,
                        alias_name=self.embedder_name + "_" + self.collection_name,
                    )
                )
            ]
        )

    # retrieve similar memories from text
    def recall_memories_from_text(self, text, metadata=None, k=5, threshold=None):
        # embed the text
        query_embedding = self.cat.embedder.embed_query(text)

        # search nearest vectors
        return self.recall_memories_from_embedding(
            query_embedding, metadata=metadata, k=k, threshold=threshold
        )

    def delete_points_by_metadata_filter(self, metadata=None):
        res = self.client.delete(
            collection_name=self.collection_name,
            points_selector=self._qdrant_filter_from_dict(metadata),
        )
        return res

    # delete point in collection
    def delete_points(self, points_ids):
        res = self.client.delete(
            collection_name=self.collection_name,
            points_selector=points_ids,
        )
        return res

    # retrieve similar memories from embedding
    def recall_memories_from_embedding(
        self, embedding, metadata=None, k=5, threshold=None
    ):
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
                    rescore=True,
                    oversampling=2.0 # Available as of v1.3.0
                )
            ),
        )

        langchain_documents_from_points = [
            (
                self._document_from_scored_point(
                    m, self.content_payload_key, self.metadata_payload_key
                ),
                m.score,
                m.vector,
                m.id,
            )
            for m in memories
        ]

        # we'll move out of langchain conventions soon and have our own cat Document
        # for doc, score, vector in langchain_documents_from_points:
        #    doc.lc_kwargs = None

        return langchain_documents_from_points

    # retrieve all the points in the collection
    def get_all_points(self):
        # retrieving the points
        all_points, _ = self.client.scroll(
            collection_name=self.collection_name,
            with_vectors=True,
            limit=10000,  # yeah, good for now dear :*
        )

        return all_points

    def db_is_remote(self):
        return isinstance(self.client._client, QdrantRemote)

    # dump collection on disk before deleting
    def save_dump(self, folder="dormouse/"):
        # only do snapshotting if using remote Qdrant
        if not self.db_is_remote():
            return

        host = self.client._client._host
        port = self.client._client._port

        if os.path.isdir(folder):
            log.info(f"Directory dormouse exists")
        else:
            log.warning(f"Directory dormouse does NOT exists, creating it.")
            os.mkdir(folder)

        self.snapshot_info = self.client.create_snapshot(
            collection_name=self.collection_name
        )
        snapshot_url_in = (
            "http://"
            + str(host)
            + ":"
            + str(port)
            + "/collections/"
            + self.collection_name
            + "/snapshots/"
            + self.snapshot_info.name
        )
        snapshot_url_out = folder + self.snapshot_info.name
        # rename snapshots for a easyer restore in the future
        alias = (
            self.client.get_collection_aliases(self.collection_name)
            .aliases[0]
            .alias_name
        )
        response = requests.get(snapshot_url_in)
        open(snapshot_url_out, "wb").write(response.content)
        new_name = folder + alias.replace("/", "-") + ".snapshot"
        os.rename(snapshot_url_out, new_name)
        for s in self.client.list_snapshots(self.collection_name):
            self.client.delete_snapshot(
                collection_name=self.collection_name, snapshot_name=s.name
            )
        log.warning(f'Dump "{new_name}" completed')
        # dump complete
