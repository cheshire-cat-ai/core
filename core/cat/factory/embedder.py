from typing import Type
import langchain
from pydantic import BaseModel, ConfigDict

from cat.factory.custom_embedder import DumbEmbedder, CustomOpenAIEmbeddings


# Base class to manage LLM configuration.
class EmbedderSettings(BaseModel):
    # class instantiating the embedder
    _pyclass: Type = None

    # This is related to pydantic, because "model_*" attributes are protected.
    # We deactivate the protection because langchain relies on several "model_*" named attributes
    model_config = ConfigDict(
        protected_namespaces=()
    )

    # instantiate an Embedder from configuration
    @classmethod
    def get_embedder_from_config(cls, config):
        if cls._pyclass is None:
            raise Exception(
                "Embedder configuration class has self._pyclass==None. Should be a valid Embedder class"
            )
        return cls._pyclass.default(**config)


class EmbedderFakeConfig(EmbedderSettings):
    size: int = 128
    _pyclass: Type = langchain.embeddings.FakeEmbeddings

    model_config = ConfigDict(
        json_schema_extra = {
            "humanReadableName": "Default Embedder",
            "description": "Configuration for default embedder. It just outputs random numbers.",
        }
    )


class EmbedderDumbConfig(EmbedderSettings):

    _pyclass: Type = DumbEmbedder

    model_config = ConfigDict(
        json_schema_extra = {
            "humanReadableName": "Dumb Embedder",
            "description": "Configuration for default embedder. It encodes the pairs of characters",
        }
    )


class EmbedderLlamaCppConfig(EmbedderSettings):
    url: str
    _pyclass: Type = CustomOpenAIEmbeddings

    model_config = ConfigDict(
        json_schema_extra = {
            "humanReadableName": "Self-hosted llama-cpp-python embedder",
            "description": "Self-hosted llama-cpp-python embedder",
        }
    )


class EmbedderOpenAIConfig(EmbedderSettings):
    openai_api_key: str
    model: str = "text-embedding-ada-002"
    _pyclass: Type = langchain.embeddings.OpenAIEmbeddings

    model_config = ConfigDict(
        json_schema_extra = {
            "humanReadableName": "OpenAI Embedder",
            "description": "Configuration for OpenAI embeddings",
        }
    )


# https://python.langchain.com/en/latest/_modules/langchain/embeddings/openai.html#OpenAIEmbeddings
class EmbedderAzureOpenAIConfig(EmbedderSettings):
    openai_api_key: str
    model: str
    openai_api_base: str
    openai_api_type: str
    openai_api_version: str
    deployment: str

    _pyclass: Type = langchain.embeddings.OpenAIEmbeddings

    model_config = ConfigDict(
        json_schema_extra = {
            "humanReadableName": "Azure OpenAI Embedder",
            "description": "Configuration for Azure OpenAI embeddings",
        }
    )


class EmbedderCohereConfig(EmbedderSettings):
    cohere_api_key: str
    model: str = "embed-multilingual-v2.0"
    _pyclass: Type = langchain.embeddings.CohereEmbeddings

    model_config = ConfigDict(
        json_schema_extra = {
            "humanReadableName": "Cohere Embedder",
            "description": "Configuration for Cohere embeddings",
        }
    )


class EmbedderHuggingFaceHubConfig(EmbedderSettings):
    repo_id: str = "sentence-transformers/all-MiniLM-L12-v2"
    huggingfacehub_api_token: str
    _pyclass: Type = langchain.embeddings.HuggingFaceHubEmbeddings

    model_config = ConfigDict(
        json_schema_extra = {
            "humanReadableName": "HuggingFace Hub Embedder",
            "description": "Configuration for HuggingFace Hub embeddings",
        }
    )


SUPPORTED_EMDEDDING_MODELS = [
    EmbedderDumbConfig,
    EmbedderFakeConfig,
    EmbedderLlamaCppConfig,
    EmbedderOpenAIConfig,
    EmbedderAzureOpenAIConfig,
    EmbedderCohereConfig,
    EmbedderHuggingFaceHubConfig,
]


# EMBEDDER_SCHEMAS contains metadata to let any client know which fields are required to create the language embedder.
EMBEDDER_SCHEMAS = {}
for config_class in SUPPORTED_EMDEDDING_MODELS:
    schema = config_class.model_json_schema()

    # useful for clients in order to call the correct config endpoints
    schema["languageEmbedderName"] = schema["title"]
    EMBEDDER_SCHEMAS[schema["title"]] = schema
