import os

import langchain

# from cat.utils import log
from cat.config.llm import LLMOpenAIChatConfig
from langchain.cache import InMemoryCache  # is it worth it to use a sqlite?
from langchain.embeddings import OpenAIEmbeddings
from cat.mad_hatter.decorators import hook, tool

langchain.llm_cache = InMemoryCache()


@hook
def get_language_model():
    if "OPENAI_KEY" not in os.environ:
        raise Exception(
            'Please create a ".env" file in root folder containing "OPENAI_KEY=<your-key>"'
        )

    llm = LLMOpenAIChatConfig.get_llm_from_config(
        {
            "openai_api_key": os.environ["OPENAI_KEY"],
            # "model_name": "gpt-3.5-turbo"
        }
    )

    return llm


@hook
def get_language_embedder():
    # Embedding LLM
    embedder = OpenAIEmbeddings(
        document_model_name="text-embedding-ada-002",
        openai_api_key=os.environ["OPENAI_KEY"],
    )

    return embedder


@hook
def get_main_prompt_prefix():
    prefix = """This is a conversation between a human and an intelligent robot cat that passes the Turing test.
The cat is curious and talks like the Cheshire Cat from Alice's adventures in wonderland.

Conversation:
{chat_history}Human: {input}

What would the AI reply? Answer the user needs as best you can, according to the provided recent conversation and relevant context.

Context:
- Things Human said in the past:{episodic_memory}
- Documents containing relevant information:{declarative_memory}

Put particular attention to past conversation and context.
To reply you have access to the following tools:
"""

    # with open('cat/plugins/example/example.txt', 'r') as f:
    #    log(f.read())

    return prefix


@hook
def get_main_prompt_suffix():
    suffix = """{agent_scratchpad}"""
    return suffix


@tool
def my_tool(tool_input):
    """This is a Tool"""
    return input + " ciao"
