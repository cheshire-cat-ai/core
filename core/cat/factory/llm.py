import langchain
from typing import Dict
import json
from pydantic import PyObject, BaseSettings

from cat.factory.custom_llm import LLMDefault, LLMCustom


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
            "name_human_readable": "Default Language Model",
            "description":
                "A dumb LLM just telling that the Cat is not configured. "
                "There will be a nice LLM here "
                "once consumer hardware allows it.",
        }


class LLMDefaultConfig(LLMSettings):
    _pyclass: PyObject = LLMDefault

    class Config:
        schema_extra = {
            "name_human_readable": "Default Language Model",
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
            "name_human_readable": "Custom LLM",
            "description": "LLM on a custom endpoint. "
                           "see docs for examples.",
        }


class LLMOpenAIChatConfig(LLMSettings):
    openai_api_key: str
    model_name: str = "gpt-3.5-turbo"
    _pyclass: PyObject = langchain.llms.OpenAIChat

    class Config:
        schema_extra = {
            "name_human_readable": "OpenAI ChatGPT",
            "description": "Chat model from OpenAI",
        }


class LLMOpenAIConfig(LLMSettings):
    openai_api_key: str
    model_name: str = "text-davinci-003"
    _pyclass: PyObject = langchain.llms.OpenAI

    class Config:
        schema_extra = {
            "name_human_readable": "OpenAI GPT-3",
            "description": "OpenAI GPT-3. More expensive but "
                           "also more flexible than ChatGPT.",
        }

        
# https://learn.microsoft.com/en-gb/azure/cognitive-services/openai/reference#chat-completions
class LLMAzureChatOpenAIConfig(LLMSettings):
    openai_api_key: str
    model_name: str = "gpt-35-turbo"  # or gpt-4, use only chat models !
    openai_api_base: str
    openai_api_type: str = "azure"
    openai_api_version: str = "2023-03-15-preview"

    deployment_name: str

    _pyclass: PyObject = langchain.chat_models.AzureChatOpenAI

    class Config:
        schema_extra = {
            "name_human_readable": "Azure OpenAI Chat Models",
            "description": "Chat model from Azure OpenAI",
        }


class LLMCohereConfig(LLMSettings):
    cohere_api_key: str
    model: str = "command"
    _pyclass: PyObject = langchain.llms.Cohere

    class Config:
        schema_extra = {
            "name_human_readable": "Cohere",
            "description": "Configuration for Cohere language model",
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
            "name_human_readable": "HuggingFace Hub",
            "description": "Configuration for HuggingFace Hub language models",
        }


class LLMHuggingFaceEndpointConfig(LLMSettings):
    endpoint_url: str
    huggingfacehub_api_token: str
    _pyclass: PyObject = langchain.llms.HuggingFaceEndpoint

    class Config:
        schema_extra = {
            "name_human_readable": "HuggingFace Endpoint",
            "description":
                "Configuration for HuggingFace Endpoint language models",
        }


# https://python.langchain.com/en/latest/modules/models/llms/integrations/azure_openai_example.html
class LLMAzureOpenAIConfig(LLMSettings):
    openai_api_key: str
    openai_api_base: str
    api_type: str = "azure"
    # https://learn.microsoft.com/en-us/azure/cognitive-services/openai/reference#completions
    # Current supported versions 2022-12-01 or 2023-03-15-preview
    api_version: str = "2023-03-15-preview"
    deployment_name: str = "text-davinci-003"
    model_name: str = "text-davinci-003"  # Use only completion models !

    _pyclass: PyObject = langchain.llms.AzureOpenAI

    class Config:
        schema_extra = {
            "name_human_readable": "Azure OpenAI Completion models",
            "description": "Configuration for Cognitive Services Azure OpenAI",
        }


SUPPORTED_LANGUAGE_MODELS = [
    LLMDefaultConfig,
    LLMCustomConfig,
    LLMOpenAIChatConfig,
    LLMOpenAIConfig,
    LLMCohereConfig,
    LLMHuggingFaceHubConfig,
    LLMHuggingFaceEndpointConfig,
    LLMAzureOpenAIConfig,
    LLMAzureChatOpenAIConfig,
]

# LLM_SCHEMAS contains metadata to let any client know
# which fields are required to create the language model.
LLM_SCHEMAS = {}
for config_class in SUPPORTED_LANGUAGE_MODELS:
    schema = config_class.schema()

    # useful for clients in order to call the correct config endpoints
    schema["languageModelName"] = schema["title"]
    LLM_SCHEMAS[schema["title"]] = schema
