import pytest

from langchain_community.llms import BaseLLM
from langchain_core.embeddings import Embeddings


from cat.looking_glass.cheshire_cat import CheshireCat
from cat.mad_hatter.mad_hatter import MadHatter
from cat.rabbit_hole import RabbitHole
from cat.memory.long_term_memory import LongTermMemory
from cat.looking_glass.agent_manager import AgentManager
from cat.factory.custom_embedder import DumbEmbedder
from cat.factory.custom_llm import LLMDefault


def get_class_from_decorated_singleton(singleton):
    return singleton().__class__


@pytest.fixture
def cheshire_cat(client):
    yield CheshireCat() # don't panic, it's a singleton

def test_main_modules_loaded(cheshire_cat):
    
    assert isinstance(
        cheshire_cat.mad_hatter,
        get_class_from_decorated_singleton(MadHatter)
    )

    assert isinstance(
        cheshire_cat.rabbit_hole,
        get_class_from_decorated_singleton(RabbitHole)
    )

    # TODO: this should be singleton too
    assert isinstance(cheshire_cat.memory, LongTermMemory)

    assert isinstance(cheshire_cat.agent_manager, AgentManager)

    assert isinstance(cheshire_cat._llm, BaseLLM)

    assert isinstance(cheshire_cat.embedder, Embeddings)


def test_default_llm_loaded(cheshire_cat):

    assert isinstance(cheshire_cat._llm, LLMDefault)
    
    out = cheshire_cat.llm("Hey")
    assert "You did not configure a Language Model" in out


def test_default_embedder_loaded(cheshire_cat):
    
    assert isinstance(cheshire_cat.embedder, DumbEmbedder)

    sentence = "I'm smarter than a random embedder BTW"
    sample_embed = DumbEmbedder().embed_query(sentence)
    out = cheshire_cat.embedder.embed_query(sentence)
    assert sample_embed == out


def test_tools_embedded(cheshire_cat):

    # get embedded tools
    tools = cheshire_cat.memory.vectors.procedural.get_all_points()
    assert len(tools) == 1

    # some check on the embedding
    assert "get_the_time" in tools[0].payload["page_content"]
    assert isinstance(tools[0].vector, list)
    sample_embed = DumbEmbedder().embed_query("I'm smarter than a random embedder BTW")
    assert len(tools[0].vector) == len(sample_embed) # right embed size
