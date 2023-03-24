import langchain
from pydantic import PyObject, BaseSettings


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


class LLMDefault(langchain.llms.base.LLM):
    @property
    def _llm_type(self):
        return ""

    def _call(self, prompt, stop=None):
        # TODO: if AI prefix in the agent changes, this will break
        return "AI: You did not configure a Language Model. Send a POST request to ... [TODO: instructions here]"


class LLMDefaultConfig(LLMSettings):
    _pyclass: PyObject = LLMDefault

    class Config:
        title = "Default LLM"
        description = "Configuration for default LLM"


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
    LLMDefaultConfig,
    LLMOpenAIConfig,
    LLMOpenAIChatConfig,
    LLMCohereChatConfig,
    LLMHuggingFacePipeline,
    LLMHuggingFaceHubConfig,
    LLMHuggingFaceEndpointConfig,
]
