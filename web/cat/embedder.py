import os

import langchain
from langchain.cache import InMemoryCache  # is it worth it to use a sqlite?
from langchain.embeddings import OpenAIEmbeddings

langchain.llm_cache = InMemoryCache()


# Embedding LLM
# TODO: should be configurable via REST API
DEFAULT_LANGUAGE_EMBEDDER = OpenAIEmbeddings(
    document_model_name="text-embedding-ada-002",
    openai_api_key=os.environ["OPENAI_KEY"],
)
