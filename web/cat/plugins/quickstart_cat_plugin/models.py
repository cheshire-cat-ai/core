import cat.config.llm as llms
import cat.config.embedder as embedders

# from cat.db import crud
# from cat.utils import log
# from cat.db.database import get_db_session
from cat.mad_hatter.decorators import hook


@hook
def get_language_model(cat):
    # TODO: give more example configurations

    # llm = LLMOpenAIChatConfig.get_llm_from_config(
    #    {
    #        "openai_api_key": os.environ["OPENAI_KEY"],
    #        # "model_name": "gpt-3.5-turbo"
    #    }
    # )

    # llm = LLMOpenAIConfig.get_llm_from_config(
    #    {
    #        "openai_api_key": os.environ["OPENAI_KEY"],
    #        # "model_name": "gpt-3.5-turbo"
    #    }
    # )

    llm = llms.LLMDefaultConfig.get_llm_from_config({})

    return llm


@hook
def get_language_embedder(cat):
    # TODO: give more example ocnfigurations

    # Embedding LLM
    # embedder = OpenAIEmbeddings(
    #    document_model_name="text-embedding-ada-002",
    #    openai_api_key=,
    # )

    embedder = embedders.EmbedderFakeConfig.get_embedder_from_config({"size": 10})

    return embedder
