import langchain
from pydantic import PyObject, BaseSettings

from cat.factory.custom_embedder import DumbEmbedder, CustomOpenAIEmbeddings
from cat.utils import check_openai_key_valid

# Base class to manage LLM configuration.
class EmbedderSettings(BaseSettings):
    # class instantiating the embedder
    _pyclass: None

    # instantiate an Embedder from configuration
    @classmethod
    def get_embedder_from_config(cls, config):
        if cls._pyclass is None:
            raise Exception(
                "Embedder configuration class has self._pyclass = None. Should be a valid Embedder class"
            )
        return cls._pyclass(**config)


class EmbedderFakeConfig(EmbedderSettings):
    size: int = 128
    _pyclass: PyObject = langchain.embeddings.FakeEmbeddings

    class Config:
        schema_extra = {
            "humanReadableName": "Default Embedder",
            "description": "Configuration for default embedder. It just outputs random numbers.",
        }


class EmbedderDumbConfig(EmbedderSettings):

    _pyclass = PyObject = DumbEmbedder

    class Config:
        schema_extra = {
            "humanReadableName": "Dumb Embedder",
            "description": "Configuration for default embedder. It encodes the pairs of characters",
        }


class EmbedderLlamaCppConfig(EmbedderSettings):
    url: str
    _pyclass = PyObject = CustomOpenAIEmbeddings

    class Config:
        schema_extra = {
            "humanReadableName": "Self-hosted llama-cpp-python embedder",
            "description": "Self-hosted llama-cpp-python embedder",
        }


class EmbedderOpenAIConfig(EmbedderSettings):
    openai_api_key: str
    model: str = "text-embedding-ada-002"
    _pyclass: PyObject = langchain.embeddings.OpenAIEmbeddings

    class Config:
        schema_extra = {
            "humanReadableName": "OpenAI Embedder",
            "description": "Configuration for OpenAI embeddings",
        }
    
    # instantiate an open ai Embedder from configuration with checking for the validity of the key
    @classmethod
    def get_embedder_from_config(cls, config):
        if cls._pyclass is None:
            raise Exception(
                "Embedder configuration class has self._pyclass = None. Should be a valid Embedder class"
            )
        check_openai_key_valid(config["openai_api_key"])
        return cls._pyclass(**config)


# https://python.langchain.com/en/latest/_modules/langchain/embeddings/openai.html#OpenAIEmbeddings
class EmbedderAzureOpenAIConfig(EmbedderSettings):
    openai_api_key: str
    model: str
    openai_api_base: str
    openai_api_type: str
    openai_api_version: str
    deployment: str

    _pyclass: PyObject = langchain.embeddings.OpenAIEmbeddings

    class Config:
        schema_extra = {
            "humanReadableName": "Azure OpenAI Embedder",
            "description": "Configuration for Azure OpenAI embeddings",
        }

    # instantiate an open ai Embedder from configuration with checking for the validity of the key
    @classmethod
    def get_embedder_from_config(cls, config):
        if cls._pyclass is None:
            raise Exception(
                "Embedder configuration class has self._pyclass = None. Should be a valid Embedder class"
            )
        check_openai_key_valid(config["openai_api_key"])
        return cls._pyclass(**config)

class EmbedderCohereConfig(EmbedderSettings):
    cohere_api_key: str
    model: str = "embed-multilingual-v2.0"
    _pyclass: PyObject = langchain.embeddings.CohereEmbeddings

    class Config:
        schema_extra = {
            "humanReadableName": "Cohere Embedder",
            "description": "Configuration for Cohere embeddings",
        }


class EmbedderHuggingFaceHubConfig(EmbedderSettings):
    repo_id: str = "sentence-transformers/all-MiniLM-L12-v2"
    huggingfacehub_api_token: str
    _pyclass: PyObject = langchain.embeddings.HuggingFaceHubEmbeddings

    class Config:
        schema_extra = {
            "humanReadableName": "HuggingFace Hub Embedder",
            "description": "Configuration for HuggingFace Hub embeddings",
        }


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
    schema = config_class.schema()

    # useful for clients in order to call the correct config endpoints
    schema["languageEmbedderName"] = schema["title"]
    EMBEDDER_SCHEMAS[schema["title"]] = schema
