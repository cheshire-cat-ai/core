import os

import langchain
from langchain.llms import OpenAIChat
from langchain.cache import InMemoryCache  # is it worth it to use a sqlite?

# from dataclasses import dataclass


# from langchain.chains import LLMChain
# from langchain.prompts import PromptTemplate
# from langchain.embeddings import OpenAIEmbeddings

langchain.llm_cache = InMemoryCache()

# TODO: abstract vendor away (no references to openai or others in this file)
if "OPENAI_KEY" not in os.environ:
    raise Exception(
        'Please create a ".env" file in root folder containing "OPENAI_KEY=<your-key>"'
    )

# Large Language Model
# TODO: should be configurable via REST API
LANGUAGE_MODEL = OpenAIChat(
    model_name="gpt-3.5-turbo", openai_api_key=os.environ["OPENAI_KEY"]
)
