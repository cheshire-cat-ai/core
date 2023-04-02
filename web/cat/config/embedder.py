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
    size: int = 10
    _pyclass: PyObject = langchain.embeddings.FakeEmbeddings

    class Config:
        title = "Default Embedder"
        description = "Configuration for default embedder"


class EmbedderOpenAIConfig(EmbedderSettings):
    openai_api_key: str
    _pyclass: PyObject = langchain.embeddings.OpenAIEmbeddings

    class Config:
        title = "OpenAI Embedder"
        description = "Configuration for OpenAI embeddings"


class EmbedderHuggingFaceHubConfig(EmbedderSettings):
    # repo_id: str = None TODO use the default sentence-transformers at the moment
    huggingfacehub_api_token: str
    _pyclass: PyObject = langchain.embeddings.HuggingFaceHubEmbeddings

    class Config:
        title = "HuggingFace Hub Embedder"
        description = "Configuration for HuggingFace Hub embeddings"


SUPPORTED_EMDEDDING_MODELS = [
    EmbedderFakeConfig,
    EmbedderOpenAIConfig,
    EmbedderHuggingFaceHubConfig,
]
