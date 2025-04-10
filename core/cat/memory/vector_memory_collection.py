import os
import uuid
from typing import Any, List, Iterable, Optional
import requests

from qdrant_client.qdrant_remote import QdrantRemote
from qdrant_client.http.models import (
    PointStruct,
    Distance,
    VectorParams,
    Filter,
    FieldCondition,
    MatchValue,
    SearchParams,
    ScalarQuantization,
    ScalarQuantizationConfig,
    ScalarType,
    QuantizationSearchParams,
    CreateAliasOperation,
    CreateAlias,
    OptimizersConfigDiff,
)

from langchain.docstore.document import Document

from cat.log import log
from cat.env import get_env


class VectorMemoryCollection:
    def __init__(
        self,
        client: Any,
        collection_name: str,
        embedder_name: str,
        embedder_size: int,
    ):
        # Set attributes (metadata on the embedder are useful because it may change at runtime)
        self.client = client
        self.collection_name = collection_name
        self.embedder_name = embedder_name
        self.embedder_size = embedder_size

        # Check if memory collection exists also in vectorDB, otherwise create it
        self.create_db_collection_if_not_exists()

        # Check db collection vector size is same as embedder size
        self.check_embedding_size()

        # log collection info
        log.debug(f"Collection {self.collection_name}:")
        log.debug(self.client.get_collection(self.collection_name))

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
            log.debug(f'Collection "{self.collection_name}" has the same embedder')
        else:
            log.warning(f'Collection "{self.collection_name}" has a different embedder')
            # Memory snapshot saving can be turned off in the .env file with:
            # SAVE_MEMORY_SNAPSHOTS=false
            if get_env("CCAT_SAVE_MEMORY_SNAPSHOTS") == "true":
                # dump collection on disk before deleting
                self.save_dump()

            self.client.delete_collection(self.collection_name)
            log.warning(f'Collection "{self.collection_name}" deleted')
            self.create_collection()

    def create_db_collection_if_not_exists(self):
        # is collection present in DB?
        collections_response = self.client.get_collections()
        for c in collections_response.collections:
            if c.name == self.collection_name:
                # collection exists. Do nothing
                log.debug(
                    f'Collection "{self.collection_name}" already present in vector store'
                )
                return

        self.create_collection()

    # create collection
    def create_collection(self):
        log.warning(f'Creating collection "{self.collection_name}" ...')
        self.client.create_collection(
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

    # adapted from https://github.com/langchain-ai/langchain/blob/bfc12a4a7644cfc4d832cc4023086a7a5374f46a/libs/langchain/langchain/vectorstores/qdrant.py#L1965
    def _qdrant_filter_from_dict(self, filter: dict) -> Filter:
        if not filter or len(filter)<1:
            return None

        return Filter(
            must=[
                condition
                for key, value in filter.items()
                for condition in self._build_condition(key, value)
            ]
        )

    # adapted from https://github.com/langchain-ai/langchain/blob/bfc12a4a7644cfc4d832cc4023086a7a5374f46a/libs/langchain/langchain/vectorstores/qdrant.py#L1941
    def _build_condition(self, key: str, value: Any) -> List[FieldCondition]:
        out = []

        if isinstance(value, dict):
            for _key, value in value.items():
                out.extend(self._build_condition(f"{key}.{_key}", value))
        elif isinstance(value, list):
            for _value in value:
                if isinstance(_value, dict):
                    out.extend(self._build_condition(f"{key}[]", _value))
                else:
                    out.extend(self._build_condition(f"{key}", _value))
        else:
            out.append(
                FieldCondition(
                    key=f"metadata.{key}",
                    match=MatchValue(value=value),
                )
            )

        return out

    def add_point(
        self,
        content: str,
        vector: Iterable,
        metadata: dict = None,
        id: Optional[str] = None,
        **kwargs: Any,
    ) -> List[str]:
        """Add a point (and its metadata) to the vectorstore.

        Args:
            content: original text.
            vector: Embedding vector.
            metadata: Optional metadata dict associated with the text.
            id:
                Optional id to associate with the point. Id has to be a uuid-like string.

        Returns:
            Point id as saved into the vectorstore.
        """

        # TODO: may be adapted to upload batches of points as langchain does.
        # Not necessary now as the bottleneck is the embedder
        point = PointStruct(
            id=id or uuid.uuid4().hex,
            payload={
                "page_content": content,
                "metadata": metadata,
            },
            vector=vector,
        )

        update_status = self.client.upsert(
            collection_name=self.collection_name, points=[point], **kwargs
        )

        if update_status.status == "completed":
            # returnign stored point
            return point # TODOV2 return internal MemoryPoint
        else:
            return None

    def delete_points_by_metadata_filter(self, metadata=None):
        res = self.client.delete(
            collection_name=self.collection_name,
            points_selector=self._qdrant_filter_from_dict(metadata),
        )
        return res

    def delete_points(self, points_ids):
        """Delete point in collection"""
        res = self.client.delete(
            collection_name=self.collection_name,
            points_selector=points_ids,
        )
        return res

    def recall_memories_from_embedding(
        self, embedding, metadata=None, k=5, threshold=None
    ):
        """Retrieve similar memories from embedding"""

        memories = self.client.query_points(
            collection_name=self.collection_name,
            query=embedding,
            query_filter=self._qdrant_filter_from_dict(metadata),
            with_payload=True,
            with_vectors=True,
            limit=k,
            score_threshold=threshold,
            search_params=SearchParams(
                quantization=QuantizationSearchParams(
                    ignore=False,
                    rescore=True,
                    oversampling=2.0,  # Available as of v1.3.0
                )
            ),
        ).points

        # convert Qdrant points to langchain.Document
        langchain_documents_from_points = []
        for m in memories:
            langchain_documents_from_points.append(
                (
                    Document(
                        page_content=m.payload.get("page_content"),
                        metadata=m.payload.get("metadata") or {},
                    ),
                    m.score,
                    m.vector,
                    m.id,
                )
            )

        # we'll move out of langchain conventions soon and have our own cat Document
        # for doc, score, vector in langchain_documents_from_points:
        #    doc.lc_kwargs = None

        return langchain_documents_from_points
    
    def get_points(self, ids: List[str]):
        """Get points by their ids."""
        return self.client.retrieve(
            collection_name=self.collection_name,
            ids=ids,
            with_vectors=True,
        )

    def get_all_points(
            self,
            limit: int = 10000,
            offset: str | None = None
        ):
        """Retrieve all the points in the collection with an optional offset and limit."""
        
        # retrieving the points
        all_points, next_page_offset = self.client.scroll(
            collection_name=self.collection_name,
            with_vectors=True,
            offset=offset,  # Start from the given offset, or the beginning if None.
            limit=limit # Limit the number of points retrieved to the specified limit.
        )

        return all_points, next_page_offset

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
            log.debug("Directory dormouse exists")
        else:
            log.info("Directory dormouse does NOT exists, creating it.")
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
