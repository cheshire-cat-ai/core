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

    def get_vector_store(self, collection_name, embeddings):
        collection_path = os.path.join(self.folder_path, collection_name)

        if self.verbose:
            log(collection_path)

        log("Loading vector store...")
        if not Path(os.path.join(collection_path, "index.pkl")).exists():
            log("index.pkl does not exist, the index is being created from scratch")
            vector_store = FAISS.from_texts(
                ["I am the Cheshire Cat"],
                embeddings,
                [
                    {
                        "who": "cheshire-cat",
                        "when": time.time(),
                        "text": "I am the Cheshire Cat",
                    }
                ],
            )
            vector_store.save_local(collection_path)
        else:
            log("Load vector store from disk")
            vector_store = FAISS.load_local(collection_path, embeddings)

        return vector_store
