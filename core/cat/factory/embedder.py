from typing import Type
import langchain
from pydantic import BaseModel, ConfigDict
from langchain.embeddings.fastembed import FastEmbedEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.embeddings import JinaEmbeddings

from cat.factory.custom_embedder import DumbEmbedder, CustomOpenAIEmbeddings
from cat.mad_hatter.mad_hatter import MadHatter


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
            "link": "",
        }
    )


class EmbedderDumbConfig(EmbedderSettings):

    _pyclass: Type = DumbEmbedder

    model_config = ConfigDict(
        json_schema_extra = {
            "humanReadableName": "Dumb Embedder",
            "description": "Configuration for default embedder. It encodes the pairs of characters",
            "link": "",
        }
    )


class EmbedderLlamaCppConfig(EmbedderSettings):
    url: str
    _pyclass: Type = CustomOpenAIEmbeddings

    model_config = ConfigDict(
        json_schema_extra = {
            "humanReadableName": "Self-hosted llama-cpp-python embedder",
            "description": "Self-hosted llama-cpp-python embedder",
            "link": "",
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
            "link": "https://platform.openai.com/docs/models/overview",
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
            "link": "https://azure.microsoft.com/en-us/products/ai-services/openai-service",
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
            "link": "https://docs.cohere.com/docs/models",
        }
    )


class EmbedderQdrantFastEmbedConfig(EmbedderSettings):
    model_name: str = "BAAI/bge-base-en"
    max_length: int = 512 # Unknown behavior for values > 512.
    doc_embed_type: str = "passage" # as suggest on fastembed documentation, "passage" is the best option for documents.
    
    _pyclass: Type = FastEmbedEmbeddings

    model_config = ConfigDict(
        json_schema_extra = {
            "humanReadableName": "Qdrant FastEmbed (Local)",
            "description": "Configuration for Qdrant FastEmbed",
            "link": "https://qdrant.github.io/fastembed/",
        }
    )
    

class EmbedderGeminiChatConfig(EmbedderSettings):
    """Configuration for Gemini Chat Embedder.

    This class contains the configuration for the Gemini Embedder.
    """
    google_api_key: str
    model_name: str = "models/embedding-001" # Default model https://python.langchain.com/docs/integrations/text_embedding/google_generative_ai
    
    _pyclass: Type = GoogleGenerativeAIEmbeddings

    model_config = ConfigDict(
        json_schema_extra = {
            "humanReadableName": "Google Gemini Embedder",
            "description": "Configuration for Gemini Embedder",
            "link": "https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/text-embeddings?hl=en",
        }
    )

class EmbedderJinaEmbeddingsConfig(EmbedderSettings):
    jina_api_key: str
    model_name: str = "jina-embeddings-v2-base-en"
    
    _pyclass: Type = JinaEmbeddings

    model_config = ConfigDict(
        json_schema_extra = {
            "humanReadableName": "Jina Embeddings",
            "description": "Configuration for Jina",
            "link": "https://jina.ai/embeddings/",
        }
    )

def get_allowed_embedder_models():

    list_embedder_default = [
        EmbedderJinaEmbeddingsConfig,
        EmbedderQdrantFastEmbedConfig,
        EmbedderOpenAIConfig,
        EmbedderAzureOpenAIConfig,
        EmbedderGeminiChatConfig,
        EmbedderLlamaCppConfig,
        EmbedderCohereConfig,
        EmbedderDumbConfig,
        EmbedderFakeConfig,
    ]

    mad_hatter_instance = MadHatter()
    list_embedder = mad_hatter_instance.execute_hook("factory_allowed_embedders", list_embedder_default, cat=None)
    return list_embedder


def get_embedder_from_name(name_embedder: str):
    """ Find the llm adapter class by name"""
    for cls in get_allowed_embedder_models():
        if cls.__name__ == name_embedder:
            return cls
    return None


def get_embedders_schemas():

    # EMBEDDER_SCHEMAS contains metadata to let any client know which fields are required to create the language embedder.
    EMBEDDER_SCHEMAS = {}
    for config_class in get_allowed_embedder_models():
        schema = config_class.model_json_schema()
        # useful for clients in order to call the correct config endpoints
        schema["languageEmbedderName"] = schema["title"]
        EMBEDDER_SCHEMAS[schema["title"]] = schema

    return EMBEDDER_SCHEMAS


