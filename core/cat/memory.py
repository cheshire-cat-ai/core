import os
import time
from pathlib import Path
from dataclasses import dataclass

from cat.utils import log
from langchain import FAISS


@dataclass
class VectorMemoryConfig:
    folder: str = os.getenv("VECTOR_STORE_FOLDER", "long_term_memory")
    verbose: bool = False


class VectorStore:
    def __init__(self, vm_config: VectorMemoryConfig) -> None:
        self.folder_path = Path(__file__).parent.parent.resolve() / vm_config.folder
        self.verbose = vm_config.verbose

    def _get_collection_path(self, collection_name):
        return self.folder_path / collection_name

    def get_vector_store(self, collection_name, embedder):
        collection_path = self._get_collection_path(collection_name)
        index_file_path = collection_path / "index.pkl"

        if self.verbose:
            log(collection_path)

        # TODO: if the embedder changed, a new vectorstore must be created
        log("Loading vector store...")
        if not index_file_path.exists():
            log("index.pkl does not exist, the index is being created from scratch")
            vector_store = FAISS.from_texts(
                ["I am the Cheshire Cat"],
                embedder,
                [
                    {
                        "who": "cheshire-cat",
                        "when": time.time(),
                        "text": "I am the Cheshire Cat",
                    }
                ],
            )
            vector_store.save_local(collection_path)
            log(f"{collection_name} vector store saved to disk")
        else:
            vector_store = FAISS.load_local(collection_path, embedder)
            log(f"{collection_name} vector store loaded from disk")

        return vector_store

    def save_vector_store(self, collection_name, vector_store):
        collection_path = self._get_collection_path(collection_name)
        vector_store.save_local(collection_path)
        log(f"{collection_name} vector store saved to disk")
