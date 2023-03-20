import os

import langchain
from cat.config.llm import LLMOpenAIChatConfig
from langchain.cache import InMemoryCache  # is it worth it to use a sqlite?
from langchain.embeddings import OpenAIEmbeddings
from cat.mad_hatter.decorators import hook

langchain.llm_cache = InMemoryCache()


@hook
def get_language_model():
    if "OPENAI_KEY" not in os.environ:
        raise Exception(
            'Please create a ".env" file in root folder containing "OPENAI_KEY=<your-key>"'
        )

    llm = LLMOpenAIChatConfig.get_llm_from_config(
        {
            "openai_api_key": os.environ["OPENAI_KEY"],
            # "model_name": "gpt-3.5-turbo"
        }
    )

    return llm


@hook
def get_language_embedder():
    # Embedding LLM
    embedder = OpenAIEmbeddings(
        document_model_name="text-embedding-ada-002",
        openai_api_key=os.environ["OPENAI_KEY"],
    )

    return embedder
