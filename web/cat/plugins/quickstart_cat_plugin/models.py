import os

import cat.config.llm as llms
import cat.config.embedder as embedders

# from cat.db import crud
# from cat.utils import log
# from cat.db.database import get_db_session
from cat.mad_hatter.decorators import hook


@hook
def get_language_model(cat):
    # TODO: give more example configurations

    if "OPENAI_KEY" in os.environ:
        llm = llms.LLMOpenAIChatConfig.get_llm_from_config(
            {
                "openai_api_key": os.environ["OPENAI_KEY"],
                # "model_name": "gpt-3.5-turbo" # TODO: allow optional kwargs
            }
        )
    elif "HF_TOKEN" in os.environ:
        if "HF_CHECKPOINT" in os.environ:
            llm = llms.LLMHuggingFaceHubConfig.get_llm_from_config(
                    {
                        "huggingfacehub_api_token": os.environ["HF_TOKEN"],
                        "repo_id" : os.environ["HF_CHECKPOINT"]
                    }
            )
        elif "HF_ENDPOINT_URL" in os.environ:
            llm = llms.LLMHuggingFaceEndpointConfig.get_llm_from_config(
                    {
                        "huggingfacehub_api_token": os.environ["HF_TOKEN"],
                        "endpoint_url" : os.environ["HF_ENDPOINT_URL"]
                    }
            )
        else:
            llm = llms.LLMHuggingFaceHubConfig.get_llm_from_config(
                    {
                        "huggingfacehub_api_token": os.environ["HF_TOKEN"],
                        "repo_id" : "google/flan-t5-xl"
                    }
            )
    else:
        llm = llms.LLMDefaultConfig.get_llm_from_config({})

    return llm


@hook
def get_language_embedder(cat):
    # TODO: give more example ocnfigurations

    # Embedding LLM

    if "OPENAI_KEY" in os.environ:
        embedder = embedders.EmbedderOpenAIConfig.get_embedder_from_config(
            {
                "openai_api_key": os.environ["OPENAI_KEY"],
                # model_name: '....'  # TODO: allow optional kwargs
            }
        )
    elif "HF_TOKEN" in os.environ:
        embedder = embedders.EmbedderHuggingFaceHubConfig.get_embedder_from_config(
            {
                "huggingfacehub_api_token": os.environ["HF_TOKEN"],
                # repo_id: "..." TODO: at the moment use default
            }
        )
    else:
        embedder = embedders.EmbedderFakeConfig.get_embedder_from_config(
            {
                "size": 1536 # mock openai embedding size
            }
        )

    return embedder
