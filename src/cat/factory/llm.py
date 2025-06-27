from langchain_openai import AzureChatOpenAI
from langchain_openai import AzureOpenAI
from langchain_community.llms import (
    HuggingFaceTextGenInference,
    HuggingFaceEndpoint,
)
from langchain_openai import ChatOpenAI, OpenAI
from langchain_cohere import ChatCohere
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic

from typing import Type
import json
from pydantic import BaseModel, ConfigDict

from cat.factory.custom_llm import LLMDefault, LLMCustom, CustomOpenAI, CustomOllama
from cat.mad_hatter.mad_hatter import MadHatter


# Base class to manage LLM configuration.
class LLMSettings(BaseModel):
    # class instantiating the model
    _pyclass: Type = None

    # This is related to pydantic, because "model_*" attributes are protected.
    # We deactivate the protection because langchain relies on several "model_*" named attributes
    model_config = ConfigDict(protected_namespaces=())

    # instantiate an LLM from configuration
    @classmethod
    def get_llm_from_config(cls, config):
        if cls._pyclass is None:
            raise Exception(
                "Language model configuration class has self._pyclass==None. Should be a valid LLM class"
            )
        return cls._pyclass.default(**config)


class LLMDefaultConfig(LLMSettings):
    _pyclass: Type = LLMDefault

    model_config = ConfigDict(
        json_schema_extra={
            "humanReadableName": "Default Language Model",
            "description": "A dumb LLM just telling that the Cat is not configured. "
            "There will be a nice LLM here once consumer hardware allows it.",
            "link": "",
        }
    )


class LLMCustomConfig(LLMSettings):
    url: str
    auth_key: str = "optional_auth_key"
    options: str = "{}"
    _pyclass: Type = LLMCustom

    # instantiate Custom LLM from configuration
    @classmethod
    def get_llm_from_config(cls, config):
        options = config["options"]
        # options are inserted as a string in the admin
        if isinstance(options, str):
            if options != "":
                config["options"] = json.loads(options)
            else:
                config["options"] = {}

        return cls._pyclass.default(**config)

    model_config = ConfigDict(
        json_schema_extra={
            "humanReadableName": "Custom LLM (Deprecated)",
            "description": "Legacy LLM adapter, you can now have it more custom in a plugin.",
            "link": "https://cheshirecat.ai/custom-large-language-model/",
        }
    )


class LLMOpenAICompatibleConfig(LLMSettings):
    url: str
    temperature: float = 0.01
    model_name: str
    api_key: str
    streaming: bool = True
    _pyclass: Type = CustomOpenAI

    model_config = ConfigDict(
        json_schema_extra={
            "humanReadableName": "OpenAI-compatible API",
            "description": "Configuration for OpenAI-compatible APIs, e.g. llama-cpp-python server, text-generation-webui, OpenRouter, TinyLLM, TogetherAI and many others.",
            "link": "",
        }
    )


class LLMOpenAIChatConfig(LLMSettings):
    openai_api_key: str
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.7
    streaming: bool = True
    _pyclass: Type = ChatOpenAI

    model_config = ConfigDict(
        json_schema_extra={
            "humanReadableName": "OpenAI ChatGPT",
            "description": "Chat model from OpenAI",
            "link": "https://platform.openai.com/docs/models/overview",
        }
    )


class LLMOpenAIConfig(LLMSettings):
    openai_api_key: str
    model_name: str = "gpt-3.5-turbo-instruct"
    temperature: float = 0.7
    streaming: bool = True
    _pyclass: Type = OpenAI

    model_config = ConfigDict(
        json_schema_extra={
            "humanReadableName": "OpenAI GPT-3",
            "description": "OpenAI GPT-3. More expensive but also more flexible than ChatGPT.",
            "link": "https://platform.openai.com/docs/models/overview",
        }
    )


# https://learn.microsoft.com/en-gb/azure/cognitive-services/openai/reference#chat-completions
class LLMAzureChatOpenAIConfig(LLMSettings):
    openai_api_key: str
    model_name: str = "gpt-35-turbo"  # or gpt-4, use only chat models !
    azure_endpoint: str
    max_tokens: int = 2048
    openai_api_type: str = "azure"
    # Dont mix api versions https://github.com/hwchase17/langchain/issues/4775
    openai_api_version: str = "2023-05-15"

    azure_deployment: str
    streaming: bool = True
    _pyclass: Type = AzureChatOpenAI

    model_config = ConfigDict(
        json_schema_extra={
            "humanReadableName": "Azure OpenAI Chat Models",
            "description": "Chat model from Azure OpenAI",
            "link": "https://azure.microsoft.com/en-us/products/ai-services/openai-service",
        }
    )


# https://python.langchain.com/en/latest/modules/models/llms/integrations/azure_openai_example.html
class LLMAzureOpenAIConfig(LLMSettings):
    openai_api_key: str
    azure_endpoint: str
    max_tokens: int = 2048
    api_type: str = "azure"
    # https://learn.microsoft.com/en-us/azure/cognitive-services/openai/reference#completions
    # Current supported versions 2022-12-01, 2023-03-15-preview, 2023-05-15
    # Don't mix api versions: https://github.com/hwchase17/langchain/issues/4775
    api_version: str = "2023-05-15"
    azure_deployment: str = "gpt-35-turbo-instruct"
    model_name: str = "gpt-35-turbo-instruct"  # Use only completion models !
    streaming: bool = True
    _pyclass: Type = AzureOpenAI

    model_config = ConfigDict(
        json_schema_extra={
            "humanReadableName": "Azure OpenAI Completion models",
            "description": "Configuration for Cognitive Services Azure OpenAI",
            "link": "https://azure.microsoft.com/en-us/products/ai-services/openai-service",
        }
    )


class LLMCohereConfig(LLMSettings):
    cohere_api_key: str
    model: str = "command"
    temperature: float = 0.7
    streaming: bool = True

    _pyclass: Type = ChatCohere

    model_config = ConfigDict(
        json_schema_extra={
            "humanReadableName": "Cohere",
            "description": "Configuration for Cohere language model",
            "link": "https://docs.cohere.com/docs/models",
        }
    )


# https://python.langchain.com/en/latest/modules/models/llms/integrations/huggingface_textgen_inference.html
class LLMHuggingFaceTextGenInferenceConfig(LLMSettings):
    inference_server_url: str
    max_new_tokens: int = 512
    top_k: int = 10
    top_p: float = 0.95
    typical_p: float = 0.95
    temperature: float = 0.01
    repetition_penalty: float = 1.03
    _pyclass: Type = HuggingFaceTextGenInference

    model_config = ConfigDict(
        json_schema_extra={
            "humanReadableName": "HuggingFace TextGen Inference",
            "description": "Configuration for HuggingFace TextGen Inference",
            "link": "https://huggingface.co/text-generation-inference",
        }
    )


# https://api.python.langchain.com/en/latest/llms/langchain_community.llms.huggingface_endpoint.HuggingFaceEndpoint.html
class LLMHuggingFaceEndpointConfig(LLMSettings):
    endpoint_url: str
    huggingfacehub_api_token: str
    task: str = "text-generation"
    max_new_tokens: int = 512
    top_k: int = None
    top_p: float = 0.95
    temperature: float = 0.8
    return_full_text: bool = False
    _pyclass: Type = HuggingFaceEndpoint

    model_config = ConfigDict(
        json_schema_extra={
            "humanReadableName": "HuggingFace Endpoint",
            "description": "Configuration for HuggingFace Endpoint language models",
            "link": "https://huggingface.co/inference-endpoints",
        }
    )


class LLMOllamaConfig(LLMSettings):
    base_url: str
    model: str = "llama3"
    num_ctx: int = 2048
    repeat_last_n: int = 64
    repeat_penalty: float = 1.1
    temperature: float = 0.8

    _pyclass: Type = CustomOllama

    model_config = ConfigDict(
        json_schema_extra={
            "humanReadableName": "Ollama",
            "description": "Configuration for Ollama",
            "link": "https://ollama.ai/library",
        }
    )


class LLMGeminiChatConfig(LLMSettings):
    """Configuration for the Gemini large language model (LLM).

    This class inherits from the `LLMSettings` class and provides default values for the following attributes:

    * `google_api_key`: The Google API key used to access the Google Natural Language Processing (NLP) API.
    * `model`: The name of the LLM model to use. In this case, it is set to "gemini".
    * `temperature`: The temperature of the model, which controls the creativity and variety of the generated responses.
    * `top_p`: The top-p truncation value, which controls the probability of the generated words.
    * `top_k`: The top-k truncation value, which controls the number of candidate words to consider during generation.
    * `max_output_tokens`: The maximum number of tokens to generate in a single response.

    The `LLMGeminiChatConfig` class is used to create an instance of the Gemini LLM model, which can be used to generate text in natural language.
    """

    google_api_key: str
    model: str = "gemini-1.5-pro-latest"
    temperature: float = 0.1
    top_p: int = 1
    top_k: int = 1
    max_output_tokens: int = 29000

    _pyclass: Type = ChatGoogleGenerativeAI

    model_config = ConfigDict(
        json_schema_extra={
            "humanReadableName": "Google Gemini",
            "description": "Configuration for Gemini",
            "link": "https://deepmind.google/technologies/gemini",
        }
    )


class LLMAnthropicChatConfig(LLMSettings):
    api_key: str
    model: str = "claude-3-5-sonnet-20241022"
    temperature: float = 0.7
    max_tokens: int = 8192
    max_retries: int = 2

    _pyclass: Type = ChatAnthropic

    model_config = ConfigDict(
        json_schema_extra={
            "humanReadableName": "Anthropic",
            "description": "Configuration for Anthropic",
            "link": "https://www.anthropic.com/",
        }
    )

def get_allowed_language_models():
    list_llms_default = [
        LLMOpenAIChatConfig,
        LLMOpenAIConfig,
        LLMOpenAICompatibleConfig,
        LLMOllamaConfig,
        LLMGeminiChatConfig,
        LLMCohereConfig,
        LLMAzureOpenAIConfig,
        LLMAzureChatOpenAIConfig,
        LLMHuggingFaceEndpointConfig,
        LLMHuggingFaceTextGenInferenceConfig,
        LLMAnthropicChatConfig,
        LLMCustomConfig,
        LLMDefaultConfig,
    ]

    mad_hatter_instance = MadHatter()
    list_llms = mad_hatter_instance.execute_hook(
        "factory_allowed_llms", list_llms_default, cat=None
    )
    return list_llms


def get_llm_from_name(name_llm: str):
    """Find the llm adapter class by name"""
    for cls in get_allowed_language_models():
        if cls.__name__ == name_llm:
            return cls
    return None


def get_llms_schemas():
    # LLM_SCHEMAS contains metadata to let any client know
    # which fields are required to create the language model.
    LLM_SCHEMAS = {}
    for config_class in get_allowed_language_models():
        schema = config_class.model_json_schema()
        # useful for clients in order to call the correct config endpoints
        schema["languageModelName"] = schema["title"]
        LLM_SCHEMAS[schema["title"]] = schema

    return LLM_SCHEMAS
