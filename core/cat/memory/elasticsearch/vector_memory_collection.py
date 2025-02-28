
import uuid
from typing import Any, List, Iterable, Mapping, Optional

from elasticsearch import Elasticsearch

from langchain.docstore.document import Document

from cat.log import log
from cat.env import get_env

from cat.memory.collection_info import CollectionInfo
from cat.memory.memory_point import MemoryPoint


class VectorMemoryCollectionES:
    def __init__(
        self,
        client: Elasticsearch,
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
        log.debug(self.get())

    def check_embedding_size(self):
        # having the same size does not necessarily imply being the same embedder
        # having vectors with the same size but from diffent embedder in the same vector space is wrong
        same_size = (
            self.get().config["params"]["vectors"]["size"]
            == self.embedder_size
        )
        alias = self.embedder_name + "_" + self.collection_name + "_" + str(self.embedder_size)
        if (self.client.indices.exists(index=alias) and same_size):
            log.debug(f'Collection "{self.collection_name}" has the same embedder')
        else:
            log.warning(f'Collection "{self.collection_name}" has different embedder')
            # Memory snapshot saving can be turned off in the .env file with:
            # SAVE_MEMORY_SNAPSHOTS=false
            if get_env("CCAT_SAVE_MEMORY_SNAPSHOTS") == "true":
                # dump collection on disk before deleting
                self.save_dump()
                log.info(f"Dump '{self.collection_name}' completed")

            self.client.indices.delete(index=self.collection_name)
            log.warning(f"Collection '{self.collection_name}' deleted")
            self.create_collection()

    def create_db_collection_if_not_exists(self):
        if not self.client.indices.exists(index=self.collection_name):
            self.create_collection()
        else:
            log.info(
                    f"Collection '{self.collection_name}' already present in vector store"
            )
            return

    # create collection
    def create_collection(self):
        mappings = {
            "mappings": {
                "properties": {
                    "page_content": {"type": "text"},
                    "vector": {
                        "type": "dense_vector",
                        "dims": self.embedder_size,
                        "index_options": {
                            "type": "int8_hnsw"
                        }
                    },
                    "metadata": {
                        "properties": {
                            "source": {"type": "keyword"},
                            "when": {"type": "date", "format": "epoch_millis"}
                        }
                    }
                }
            }
        }
        log.warning(f"Creating collection '{self.collection_name}' ...")
        self.client.indices.create(index=self.collection_name, body=mappings)

        self.client.indices.put_alias(
            index=self.collection_name,
            name=self.embedder_name + "_" + self.collection_name + "_" + str(self.embedder_size)
        )


    def _es_filter_from_dict(self, filter: dict) -> Mapping[str, Mapping[str, Any]]:
        if not filter or len(filter)<1:
            return None

        return {
            "must": [
                condition
                for key, value in filter.items()
                for condition in self._build_condition(key, value)
            ]
        }

    def _build_condition(self, key: str, value: Any) -> dict[str, str | int | float]:
        out = []

        if isinstance(value, dict):
            for _key, value in value.items():
                out.extend(self._build_condition(f"{key}.{_key}", value))
        elif isinstance(value, list):
            for _value in value:
                out.extend(self._build_condition(f"{key}", _value))
        else:
            out.append({f"{key}": value})

        return out

    def add_point(
        self,
        content: str,
        vector: Iterable,
        metadata: dict = None,
        id: Optional[str] = None,
        **kwargs: Any,
    ) -> List[str]:
        """Add a document (and its metadata) to the vectorstore.

        Args:
            content: original text.
            vector: Embedding vector.
            metadata: Optional metadata dict associated with the text.
            id:
                Optional id to associate with the point. Id has to be a uuid-like string.

        Returns:
            Point id as saved into the vectorstore.
        """

        pointId = id or uuid.uuid4().hex

        # Use the single create for now
        # TODO: will use the bulk later
        update_status = self.client.create(
            index=self.collection_name,
            id=pointId,
            document={
                "page_content": content,
                "vector": vector,
                "metadata": {
                    "source": metadata["source"],
                    "when": int(metadata["when"])
                },
            })
        
        status = update_status["result"] if update_status else None
        print(status)
        if status and status == "completed" or status == "updated":
            # returnign stored point
            return MemoryPoint(
                id=pointId,
                vector=vector,
                payload={
                    "page_content": content,
                    "metadata": metadata,
                })
        else:
            return None

    def delete_points_by_metadata_filter(self, metadata=None):
        res = self.client.delete_by_query(
            index = self.collection_name,
            query={
                "bool": self._es_filter_from_dict(metadata)
            }
        )
        return res

    def delete_points(self, points_ids):
        """Delete point in collection"""
        operations = []
        for point_id in points_ids:
            operations.append({"delete": {"_index": self.collection_name, "_id": point_id}})

        res = self.client.bulk(
            index=self.collection_name,
            operations=operations,
        )
        return res

    def recall_memories_from_embedding(
        self, embedding, metadata=None, k=5, threshold=None
    ):
        """Retrieve similar memories from embedding"""

        knn_params = {
                "field": "vector",
                "query_vector":embedding,
                "k":k
            }
        if threshold is not None:
            knn_params["similarity"] = threshold

        memories = self.client.search(
            index=self.collection_name,
            knn= knn_params
        )


        # convert ES points to langchain.Document
        langchain_documents_from_points = []
        for m in memories['hits']["hits"]:
            langchain_documents_from_points.append(
                (
                    Document(
                        page_content=m["_source"]["page_content"],
                        metadata=m["_source"]["metadata"] or {},
                    ),
                    m["_score"],
                    m["_source"]["vector"],
                    m["_id"],
                )
            )
        print(langchain_documents_from_points)

        return langchain_documents_from_points
    
    def get_points(self, ids: List[str]):
        """Get points by their ids."""
        result = self.client.mget(index=self.collection_name, ids=ids)
        return map(lambda x: MemoryPoint(x.id, x.vector, x.payload), result['hits']['hits'])

    def get_all_points(
            self,
            limit: int = 10000,
            offset: str | None = None
        ):
        """Retrieve all the points in the collection with an optional offset and limit."""
        results = self.client.search(index=self.collection_name, from_=offset, size=limit)

        next_offset = offset + limit if offset else limit

        # Remap the points to MemoryPoint objects
        all_points =[MemoryPoint(
            id=x["_id"],
            vector=x["_source"]["vector"],
            payload={
                "page_content": x["_source"]["page_content"],
                "metadata": x["_source"]["metadata"]
            }
        ) for x in results['hits']['hits']]

        return all_points, next_offset

    def db_is_remote(self):
        return True

    # dump collection on disk before deleting
    def save_dump(self, folder="dormouse/"):
        # # only do snapshotting if using remote Qdrant
        if not self.db_is_remote():
            return

        # host = self.client._client._host
        # port = self.client._client._port

        # if os.path.isdir(folder):
        #     log.info("Directory dormouse exists")
        # else:
        #     log.warning("Directory dormouse does NOT exists, creating it.")
        #     os.mkdir(folder)

        # self.snapshot_info = self.client.create_snapshot(
        #     collection_name=self.collection_name
        # )
        # snapshot_url_in = (
        #     "http://"
        #     + str(host)
        #     + ":"
        #     + str(port)
        #     + "/collections/"
        #     + self.collection_name
        #     + "/snapshots/"
        #     + self.snapshot_info.name
        # )
        # snapshot_url_out = folder + self.snapshot_info.name
        # # rename snapshots for a easyer restore in the future
        # alias = (
        #     self.client.get_collection_aliases(self.collection_name)
        #     .aliases[0]
        #     .alias_name
        # )
        # response = requests.get(snapshot_url_in)
        # open(snapshot_url_out, "wb").write(response.content)
        # new_name = folder + alias.replace("/", "-") + ".snapshot"
        # os.rename(snapshot_url_out, new_name)
        # for s in self.client.list_snapshots(self.collection_name):
        #     self.client.delete_snapshot(
        #         collection_name=self.collection_name, snapshot_name=s.name
        #     )
        # log.warning(f'Dump "{new_name}" completed')


    def delete(self):
        """Delete the collection from the vectorstore."""
        return self.client.indices.delete(index=self.collection_name)
    
    def get(self):
        """Get the collection from the vectorstore."""

        return CollectionInfo(self.client.esql.query(query = f"FROM {self.collection_name} | STATS COUNT()")["values"][0][0], self.embedder_size)