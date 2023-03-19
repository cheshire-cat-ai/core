import abc
from dataclasses import dataclass
import enum
from logging import warning
import os
from typing import List, Tuple

import langchain
from langchain.llms import OpenAIChat
from langchain.embeddings import OpenAIEmbeddings
from langchain.cache import InMemoryCache
from langchain.llms.openai import OpenAIChat
from langchain.embeddings.base import Embeddings
from langchain.llms.base import BaseLLM

from web.cat.exceptions.llm_exception import NoModelKeyProvided

langchain.llm_cache = InMemoryCache()


class SupportedVendor(enum.Enum):
    OPENAI = "OPENAI"


def get_models(
    vendor: SupportedVendor, llm_name: str, embedder_name: str, model_key: str = None
) -> Tuple[BaseLLM, Embeddings]:
    if vendor == SupportedVendor.OPENAI:
        if not model_key:
            NoModelKeyProvided()
        return OpenAIChat(model_name=llm_name, model_key=model_key), OpenAIEmbeddings(
            model_name=embedder_name, model_key=model_key
        )
