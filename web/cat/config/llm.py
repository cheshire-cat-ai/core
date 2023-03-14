import os

import langchain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAIChat
from langchain.chains import LLMChain
from langchain.embeddings import OpenAIEmbeddings
from langchain.cache import InMemoryCache # is it worth it to use a sqlite?
langchain.llm_cache = InMemoryCache()

# TODO: abstract vendor away (no references to openai or others in this file)
import openai
if not 'OPENAI_KEY' in os.environ:
    raise Exception('Please create a ".env" file in root folder containing "OPENAI_KEY=<your-key>"')

#### Large Language Model
# TODO: should be configurable via REST API
LANGUAGE_MODEL = OpenAIChat(
    model_name='gpt-3.5-turbo',
    openai_api_key=os.environ['OPENAI_KEY']
)

### Embedding LLM
# TODO: should be configurable via REST API
LANGUAGE_EMBEDDER = OpenAIEmbeddings(
    document_model_name='text-embedding-ada-002',
    openai_api_key=os.environ['OPENAI_KEY']
)

