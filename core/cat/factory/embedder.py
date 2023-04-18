import langchain
from pydantic import PyObject, BaseSettings


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
    size: int = 1536
    _pyclass: PyObject = langchain.embeddings.FakeEmbeddings

    class Config:
        schema_extra = {
            "name_human_readable": "Default Embedder",
            "description": "Configuration for default embedder. It just outputs random numbers XD",
        }


class EmbedderOpenAIConfig(EmbedderSettings):
    openai_api_key: str
    _pyclass: PyObject = langchain.embeddings.OpenAIEmbeddings

    class Config:
        schema_extra = {
            "name_human_readable": "OpenAI Embedder",
            "description": "Configuration for OpenAI embeddings",
        }

class EmbedderAzureOpenAIConfig(EmbedderSettings):
    openai_api_key: str
    model_name: str
    api_base: str
    api_type: str
    api_version: str
    deployment_name: str

    _pyclass: PyObject = langchain.embeddings.FakeEmbeddings

    class Config:
        schema_extra = {
            "name_human_readable": "Azure OpenAI Embedder",
            "description": "Configuration for Azure OpenAI embeddings",
        }


class EmbedderCohereConfig(EmbedderSettings):
    cohere_api_key: str
    _pyclass: PyObject = langchain.embeddings.CohereEmbeddings

    class Config:
        schema_extra = {
            "name_human_readable": "Cohere Embedder",
            "description": "Configuration for Cohere embeddings",
        }


class EmbedderHuggingFaceHubConfig(EmbedderSettings):
    repo_id: str
    huggingfacehub_api_token: str
    _pyclass: PyObject = langchain.embeddings.HuggingFaceHubEmbeddings

    class Config:
        schema_extra = {
            "name_human_readable": "HuggingFace Hub Embedder",
            "description": "Configuration for HuggingFace Hub embeddings",
        }


SUPPORTED_EMDEDDING_MODELS = [
    EmbedderFakeConfig,
    EmbedderOpenAIConfig,
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
