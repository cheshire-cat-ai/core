"""Hooks to modify the Cat's language and embedding models.

Here is a collection of methods to hook into the settings of the Large Language Model and the Embedder.

"""

import os

import cat.factory.llm as llms
import cat.factory.embedder as embedders
from cat.db import crud
from langchain.llms import Cohere, OpenAI, OpenAIChat, AzureOpenAI, HuggingFaceTextGenInference
from langchain.chat_models import ChatOpenAI
from langchain.base_language import BaseLanguageModel
from langchain import HuggingFaceHub
from langchain.chat_models import AzureChatOpenAI
from cat.mad_hatter.decorators import hook


@hook(priority=0)
def get_language_model(cat) -> BaseLanguageModel:
    """Hook into the Large Language Model (LLM) selection.

    Allows to modify how the Cat selects the LLM at bootstrap time.

    Parameters
    ----------
    cat: CheshireCat
        Cheshire Cat instance.

    Returns
    -------
    lll : BaseLanguageModel
        Langchain `BaseLanguageModel` instance of the selected model.

    Notes
    -----
    Bootstrapping is the process of loading the plugins, the natural language objects (e.g. the LLM), the memories,
    the *Agent Manager* and the *Rabbit Hole*.

    """
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
        try:
            llm = FactoryClass.get_llm_from_config(selected_llm_config.value)
        except Exception as e:
            import traceback
            traceback.print_exc()
            llm = llms.LLMDefaultConfig.get_llm_from_config({})
            

    return llm


@hook(priority=0)
def get_language_embedder(cat) -> embedders.EmbedderSettings:
    """Hook into the  embedder selection.

    Allows to modify how the Cat selects the embedder at bootstrap time.

    Bootstrapping is the process of loading the plugins, the natural language objects (e.g. the LLM),
    the memories, the *Agent Manager* and the *Rabbit Hole*.

    Parameters
    ----------
    cat: CheshireCat
        Cheshire Cat instance.

    Returns
    -------
    embedder : Embeddings
        Selected embedder model.
    """
    # Embedding LLM

    selected_embedder = crud.get_setting_by_name(next(cat.db()), name="embedder_selected")

    if selected_embedder is not None:

        # get Embedder factory class
        selected_embedder_class = selected_embedder.value["name"]
        FactoryClass = getattr(embedders, selected_embedder_class)

        # obtain configuration and instantiate Embedder
        selected_embedder_config = crud.get_setting_by_name(
            next(cat.db()), name=selected_embedder_class
        )
        embedder = FactoryClass.get_embedder_from_config(selected_embedder_config.value)
        
        return embedder


    print("naked cat: ", cat._llm)

    # OpenAI embedder
    if type(cat._llm) in [OpenAI, OpenAIChat, ChatOpenAI]:
        embedder = embedders.EmbedderOpenAIConfig.get_embedder_from_config(
            {
                "openai_api_key": cat._llm.openai_api_key,
            }
        )

    # Azure
    elif type(cat._llm) in [AzureOpenAI, AzureChatOpenAI]:
        embedder = embedders.EmbedderAzureOpenAIConfig.get_embedder_from_config(
            {
                "openai_api_key": cat._llm.openai_api_key,
                "openai_api_type": "azure",
                "model": "text-embedding-ada-002",
                # Now the only model for embeddings is text-embedding-ada-002
                # It is also possible to use the Azure "deployment" name that is user defined
                # when the model is deployed to Azure.
                # "deployment": "my-text-embedding-ada-002",
                "openai_api_base": cat._llm.openai_api_base,
                # https://learn.microsoft.com/en-us/azure/cognitive-services/openai/reference#embeddings
                # current supported versions 2022-12-01,2023-03-15-preview, 2023-05-15
                # Don't mix api versions https://github.com/hwchase17/langchain/issues/4775
                "openai_api_version": "2023-05-15",
            }
        )

    # Cohere
    elif type(cat._llm) in [Cohere]:
        embedder = embedders.EmbedderCohereConfig.get_embedder_from_config(
            {
                "cohere_api_key": cat._llm.cohere_api_key,
                "model": "embed-multilingual-v2.0",
                # Now the best model for embeddings is embed-multilingual-v2.0

            }
        )

    # HuggingFace
    elif type(cat._llm) in [HuggingFaceHub]:
        embedder = embedders.EmbedderHuggingFaceHubConfig.get_embedder_from_config(
                {
                    "huggingfacehub_api_token": cat._llm.huggingfacehub_api_token,
                    "repo_id": "sentence-transformers/all-mpnet-base-v2",
                }
            )
    # elif "HF_TOKEN" in os.environ:
      #   if "HF_EMBEDDER" in os.environ:
        #     embedder = embedders.EmbedderHuggingFaceHubConfig.get_embedder_from_config(
        #         {
        #             "huggingfacehub_api_token": os.environ["HF_TOKEN"],
        #             "repo_id": os.environ["HF_EMBEDDER"],
        #         }
        #     )
        # else:
        #     embedder = embedders.EmbedderHuggingFaceHubConfig.get_embedder_from_config(
        #         {
        #             "huggingfacehub_api_token": os.environ["HF_TOKEN"],
        #             # repo_id: "..." TODO: at the moment use default
        #         }
        #     )
    else:
        embedder = embedders.EmbedderFakeConfig.get_embedder_from_config(
            {"size": 128}  # mock openai embedding size
        )

    return embedder