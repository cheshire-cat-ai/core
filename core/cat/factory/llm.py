import langchain
from typing import Dict, List
import json
from pydantic import PyObject, BaseSettings

from cat.factory.custom_llm import LLMDefault, LLMCustom, CustomOpenAI


# Base class to manage LLM configuration.
class LLMSettings(BaseSettings):
    # class instantiating the model
    _pyclass: None

    # instantiate an LLM from configuration
    @classmethod
    def get_llm_from_config(cls, config):
        if cls._pyclass is None:
            raise Exception(
                "Language model configuration class has self._pyclass = None. "
                "Should be a valid LLM class"
            )
        return cls._pyclass(**config)


class LLMDefaultConfig(LLMSettings):
    _pyclass: PyObject = LLMDefault

    class Config:
        schema_extra = {
            "humanReadableName": "Default Language Model",
            "description":
                "A dumb LLM just telling that the Cat is not configured. "
                "There will be a nice LLM here "
                "once consumer hardware allows it.",
        }


class LLMCustomConfig(LLMSettings):

    url: str
    auth_key: str = "optional_auth_key"
    options: str = "{}"
    _pyclass: PyObject = LLMCustom

    # instantiate Custom LLM from configuration
    @classmethod
    def get_llm_from_config(cls, config):
        # options are inserted as a string in the admin
        if type(config["options"]) == str:
            config["options"] = json.loads(config["options"])

        return cls._pyclass(**config)

    class Config:
        schema_extra = {
            "humanReadableName": "Custom LLM",
            "description": 
                "LLM on a custom endpoint. "
                "See docs for examples.",
        }


class LLMLlamaCppConfig(LLMSettings):
    url: str
    temperature: float = 0.01
    max_tokens: int = 512
    stop: str = "Human:,###"
    top_k: int = 40
    top_p: float = 0.95
    repeat_penalty: float = 1.1
    _pyclass: PyObject = CustomOpenAI

    class Config:
        schema_extra = {
            "humanReadableName": "Self-hosted llama-cpp-python",
            "description": "Self-hosted llama-cpp-python compatible LLM",
        }

class LLMOpenAIChatConfig(LLMSettings):
    openai_api_key: str
    model_name: str = "gpt-3.5-turbo"
    _pyclass: PyObject = langchain.chat_models.ChatOpenAI

    class Config:
        schema_extra = {
            "humanReadableName": "OpenAI ChatGPT",
            "description": "Chat model from OpenAI",
        }


class LLMOpenAIConfig(LLMSettings):
    openai_api_key: str
    model_name: str = "text-davinci-003"
    _pyclass: PyObject = langchain.llms.OpenAI

    class Config:
        schema_extra = {
            "humanReadableName": "OpenAI GPT-3",
            "description": 
                "OpenAI GPT-3. More expensive but "
                "also more flexible than ChatGPT.",
        }


# https://learn.microsoft.com/en-gb/azure/cognitive-services/openai/reference#chat-completions
class LLMAzureChatOpenAIConfig(LLMSettings):
    openai_api_key: str
    model_name: str = "gpt-35-turbo"  # or gpt-4, use only chat models !
    openai_api_base: str
    openai_api_type: str = "azure"
    # Dont mix api versions https://github.com/hwchase17/langchain/issues/4775
    openai_api_version: str = "2023-05-15"

    deployment_name: str

    _pyclass: PyObject = langchain.chat_models.AzureChatOpenAI

    class Config:
        schema_extra = {
            "humanReadableName": "Azure OpenAI Chat Models",
            "description": "Chat model from Azure OpenAI",
        }


# https://python.langchain.com/en/latest/modules/models/llms/integrations/azure_openai_example.html
class LLMAzureOpenAIConfig(LLMSettings):
    openai_api_key: str
    openai_api_base: str
    api_type: str = "azure"
    # https://learn.microsoft.com/en-us/azure/cognitive-services/openai/reference#completions
    # Current supported versions 2022-12-01, 2023-03-15-preview, 2023-05-15
    # Don't mix api versions: https://github.com/hwchase17/langchain/issues/4775
    api_version: str = "2023-05-15"
    deployment_name: str = "text-davinci-003"
    model_name: str = "text-davinci-003"  # Use only completion models !

    _pyclass: PyObject = langchain.llms.AzureOpenAI

    class Config:
        schema_extra = {
            "humanReadableName": "Azure OpenAI Completion models",
            "description": "Configuration for Cognitive Services Azure OpenAI",
        }


class LLMCohereConfig(LLMSettings):
    cohere_api_key: str
    model: str = "command"
    _pyclass: PyObject = langchain.llms.Cohere

    class Config:
        schema_extra = {
            "humanReadableName": "Cohere",
            "description": "Configuration for Cohere language model",
        }

# https://python.langchain.com/en/latest/modules/models/llms/integrations/huggingface_textgen_inference.html
class LLMHuggingFaceTextGenInferenceConfig(LLMSettings):
    inference_server_url: str
    max_new_tokens: int = 512
    top_k: int = 10
    top_p: float = 0.95
    typical_p: float = 0.95
    temperature: float = 0.01
    repetition_penalty: float = 1.03
    _pyclass: PyObject = langchain.llms.HuggingFaceTextGenInference

    class Config:
        schema_extra = {
            "humanReadableName": "HuggingFace TextGen Inference",
            "description": "Configuration for HuggingFace TextGen Inference",
        }

class LLMHuggingFaceHubConfig(LLMSettings):
    # model_kwargs = {
    #    "generation_config": {
    #        "min_new_tokens": 10000
    #    }
    # }
    repo_id: str
    huggingfacehub_api_token: str
    _pyclass: PyObject = langchain.llms.HuggingFaceHub

    class Config:
        schema_extra = {
            "humanReadableName": "HuggingFace Hub",
            "description": "Configuration for HuggingFace Hub language models",
        }


class LLMHuggingFaceEndpointConfig(LLMSettings):
    endpoint_url: str
    huggingfacehub_api_token: str
    task: str = "text2text-generation"
    _pyclass: PyObject = langchain.llms.HuggingFaceEndpoint

    class Config:
        schema_extra = {
            "humanReadableName": "HuggingFace Endpoint",
            "description":
                "Configuration for HuggingFace Endpoint language models",
        }


class LLMAnthropicConfig(LLMSettings):
    anthropic_api_key: str
    model: str = "claude-v1"
    _pyclass: PyObject = langchain.chat_models.ChatAnthropic

    class Config:
        schema_extra = {
            "humanReadableName": "Anthropic",
            "description": "Configuration for Anthropic language model",
        }


class LLMGooglePalmConfig(LLMSettings):
    google_api_key: str
    model_name: str = "models/text-bison-001"
    _pyclass: PyObject = langchain.llms.GooglePalm

    class Config:
        schema_extra = {
            "humanReadableName": "Google PaLM",
            "description": "Configuration for Google PaLM language model",
        }


SUPPORTED_LANGUAGE_MODELS = [
    LLMDefaultConfig,
    LLMCustomConfig,
    LLMLlamaCppConfig,
    LLMOpenAIChatConfig,
    LLMOpenAIConfig,
    LLMCohereConfig,
    LLMHuggingFaceHubConfig,
    LLMHuggingFaceEndpointConfig,
    LLMHuggingFaceTextGenInferenceConfig,
    LLMAzureOpenAIConfig,
    LLMAzureChatOpenAIConfig,
    LLMAnthropicConfig,
    LLMGooglePalmConfig
]

# LLM_SCHEMAS contains metadata to let any client know
# which fields are required to create the language model.
LLM_SCHEMAS = {}
for config_class in SUPPORTED_LANGUAGE_MODELS:
    schema = config_class.schema()

    # useful for clients in order to call the correct config endpoints
    schema["languageModelName"] = schema["title"]
    LLM_SCHEMAS[schema["title"]] = schema
