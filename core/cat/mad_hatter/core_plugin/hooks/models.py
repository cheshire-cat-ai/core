import os

import cat.factory.llm as llms
import cat.factory.embedder as embedders
from cat.db import crud
from langchain.llms import OpenAI, OpenAIChat, AzureOpenAI
from cat.mad_hatter.decorators import hook


@hook(priority=0)
def get_language_model(cat):
    selected_llm = crud.get_setting_by_name(next(cat.db()), name="llm_selected")

    if selected_llm is None:
        # return default LLM
        llm = llms.LLMDefaultConfig.get_llm_from_config({})

    else:
        # get LLM factory class
        selected_llm_class = selected_llm.value["name"]
        FactoryClass = getattr(llms, selected_llm_class)

        # obtain configuration and instantiate LLM
        selected_llm_config = crud.get_setting_by_name(
            next(cat.db()), name=selected_llm_class
        )
        llm = FactoryClass.get_llm_from_config(selected_llm_config.value)

    return llm


"""
    if "OPENAI_KEY" in os.environ:
        llm = llms.LLMOpenAIChatConfig.get_llm_from_config(
            {
                "openai_api_key": os.environ["OPENAI_KEY"],
                # "model_name": "gpt-3.5-turbo" # TODO: allow optional kwargs
            }
        )
    elif "COHERE_KEY" in os.environ:
        llm = llms.LLMCohereConfig.get_llm_from_config(
            {"cohere_api_key": os.environ["COHERE_KEY"], "model": "command"}
        )
    elif "HF_TOKEN" in os.environ:
        if "HF_CHECKPOINT" in os.environ:
            llm = llms.LLMHuggingFaceHubConfig.get_llm_from_config(
                {
                    "huggingfacehub_api_token": os.environ["HF_TOKEN"],
                    "repo_id": os.environ["HF_CHECKPOINT"],
                }
            )
        elif "HF_ENDPOINT_URL" in os.environ:
            llm = llms.LLMHuggingFaceEndpointConfig.get_llm_from_config(
                {
                    "huggingfacehub_api_token": os.environ["HF_TOKEN"],
                    "endpoint_url": os.environ["HF_ENDPOINT_URL"],
                }
            )
        else:
            llm = llms.LLMHuggingFaceHubConfig.get_llm_from_config(
                {
                    "huggingfacehub_api_token": os.environ["HF_TOKEN"],
                    "repo_id": "google/flan-t5-xl",
                }
            )
    else:
        llm = llms.LLMDefaultConfig.get_llm_from_config({})

    return llm
"""


@hook(priority=0)
def get_language_embedder(cat):
    # TODO: give more example configurations

    # Embedding LLM
    using_openai_llm = type(cat.llm) in [OpenAI, OpenAIChat, AzureOpenAI]
    if ("OPENAI_KEY" in os.environ) or using_openai_llm:
        openai_key = os.getenv("OPENAI_KEY")
        if openai_key is None:
            openai_key = cat.llm.openai_api_key
        if using_openai_llm in [OpenAI, OpenAIChat]:
            embedder = embedders.EmbedderOpenAIConfig.get_embedder_from_config(
                {
                   "openai_api_key": openai_key,
                   # model_name: '....'  # TODO: allow optional kwargs
                }
            )
        else:
            embedder = embedders.EmbedderAzureOpenAIConfig.get_embedder_from_config(
                {
                   "openai_api_key": openai_key,
                   "openai_api_type": "azure",
                   "model": "text-embedding-ada-002",
                   # Now the only model for embeddings is text-embedding-ada-002
                   # It is also possible to use the Azure "deployment" name that is user defined
                   # when the model is deployed to Azure.
                   # "deployment": "my-text-embedding-ada-002",
                   "openai_api_base": cat.llm.openai_api_base,
                   # https://learn.microsoft.com/en-us/azure/cognitive-services/openai/reference#embeddings
                   # current supported versions 2022-12-01 or 2023-03-15-preview
                   "openai_api_version": "2022-12-01",
                }
            )
    elif "COHERE_KEY" in os.environ:
        embedder = embedders.EmbedderCohereConfig.get_embedder_from_config(
            {"cohere_api_key": os.environ["COHERE_KEY"]}
        )
    elif "HF_TOKEN" in os.environ:
        if "HF_EMBEDDER" in os.environ:
            embedder = embedders.EmbedderHuggingFaceHubConfig.get_embedder_from_config(
                {
                    "huggingfacehub_api_token": os.environ["HF_TOKEN"],
                    "repo_id": os.environ["HF_EMBEDDER"],
                }
            )
        else:
            embedder = embedders.EmbedderHuggingFaceHubConfig.get_embedder_from_config(
                {
                    "huggingfacehub_api_token": os.environ["HF_TOKEN"],
                    # repo_id: "..." TODO: at the moment use default
                }
            )
    else:
        embedder = embedders.EmbedderFakeConfig.get_embedder_from_config(
            {"size": 1536}  # mock openai embedding size
        )

    return embedder
