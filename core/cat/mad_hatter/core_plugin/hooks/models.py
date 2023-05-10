import os

import cat.factory.llm as llms
import cat.factory.embedder as embedders
from cat.db import crud
from langchain.llms import Cohere, OpenAI, OpenAIChat, AzureOpenAI
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


@hook(priority=0)
def get_language_embedder(cat):
    # Embedding LLM

    # OpenAI embedder
    if type(cat.llm) in [OpenAI, OpenAIChat]:
        embedder = embedders.EmbedderOpenAIConfig.get_embedder_from_config(
            {"openai_api_key": cat.llm.openai_api_key}
        )

    # Azure
    elif type(cat.llm) in [AzureOpenAI]:
        embedder = embedders.EmbedderAzureOpenAIConfig.get_embedder_from_config(
            {
                "openai_api_key": cat.llm.openai_api_key,
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

    # Cohere
    elif type(cat.llm) in [Cohere]:
        embedder = embedders.EmbedderCohereConfig.get_embedder_from_config(
            {"cohere_api_key": cat.llm.cohere_api_key}
        )

    # HuggingFace # TODO: avoid using env variables
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
