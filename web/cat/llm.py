import os

import langchain
from pydantic import PyObject, BaseSettings
from langchain.cache import InMemoryCache

langchain.llm_cache = InMemoryCache()


# Base class to manage LLM configuration.
class LLMSettings(BaseSettings):
    # class instantiating the model
    _pyclass: None

    # instantiate an LLM from configuration
    @classmethod
    def get_llm_from_config(cls, config):
        if cls._pyclass is None:
            raise Exception(
                "Language model configuration class has self._pyclass = None. Should be a valid LLM class"
            )
        return cls._pyclass(**config)


class LLMOpenAIConfig(LLMSettings):
    openai_api_key: str
    _pyclass: PyObject = langchain.llms.OpenAI

    class Config:
        title = "OpenAI GPT-3.5"
        description = "Configuration for OpenAI completion models"


class LLMOpenAIChatConfig(LLMSettings):
    openai_api_key: str
    _pyclass: PyObject = langchain.llms.OpenAIChat

    class Config:
        title = "OpenAI ChatGPT"
        description = "Configuration for OpenAI chat models"


class LLMCohereChatConfig(LLMSettings):
    cohere_api_key: str
    _pyclass: PyObject = langchain.llms.Cohere

    class Config:
        title = "Cohere"
        description = "Configuration for Cohere language models"


class LLMHuggingFacePipeline(LLMSettings):
    model_id: str
    _pyclass: PyObject = langchain.llms.HuggingFacePipeline

    class Config:
        title = "HuggingFace (local model)"
        description = "Configuration for HuggingFace Hub language models"


class LLMHuggingFaceHubConfig(LLMSettings):
    repo_id: str
    huggingfacehub_api_token: str
    _pyclass: PyObject = langchain.llms.HuggingFaceHub

    class Config:
        title = "HuggingFace Hub"
        description = "Configuration for HuggingFace Hub language models"


class LLMHuggingFaceEndpointConfig(LLMSettings):
    endpoint_url: str
    huggingfacehub_api_token: str
    _pyclass: PyObject = langchain.llms.HuggingFaceEndpoint

    class Config:
        title = "HuggingFace Endpoint"
        description = "Configuration for HuggingFace Endpoint language models"


SUPPORTED_LANGUAGE_MODELS = [
    LLMOpenAIConfig,
    LLMOpenAIChatConfig,
    LLMCohereChatConfig,
    LLMHuggingFacePipeline,
    LLMHuggingFaceHubConfig,
    LLMHuggingFaceEndpointConfig,
]


# TODO: this is a temp way of starting the cat directly with openai chatGPT
# the cat shohuld start with a light weight LM and wait to be configured with a better one
if "OPENAI_KEY" not in os.environ:
    raise Exception(
        'Please create a ".env" file in root folder containing "OPENAI_KEY=<your-key>"'
    )

DEFAULT_LANGUAGE_MODEL = LLMOpenAIChatConfig.get_llm_from_config(
    {
        "openai_api_key": os.environ["OPENAI_KEY"],
        # "model_name": "gpt-3.5-turbo"
    }
)
