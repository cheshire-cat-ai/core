import pytest

from langchain_community.llms import BaseLLM
from langchain_core.embeddings import Embeddings


from cat.looking_glass.cheshire_cat import CheshireCat
from cat.mad_hatter.mad_hatter import MadHatter
from cat.rabbit_hole import RabbitHole
from cat.memory.long_term_memory import LongTermMemory
from cat.agents.main_agent import MainAgent
from cat.factory.custom_embedder import DumbEmbedder
from cat.factory.custom_llm import LLMDefault


def get_class_from_decorated_singleton(singleton):
    return singleton().__class__


@pytest.fixture(scope="function")
def cheshire_cat(client):
    yield CheshireCat()  # don't panic, it's a singleton


def test_main_modules_loaded(cheshire_cat):
    assert isinstance(
        cheshire_cat.mad_hatter, get_class_from_decorated_singleton(MadHatter)
    )

    assert isinstance(
        cheshire_cat.rabbit_hole, get_class_from_decorated_singleton(RabbitHole)
    )

    # TODO: this should be singleton too
    assert isinstance(cheshire_cat.memory, LongTermMemory)

    assert isinstance(cheshire_cat.main_agent, MainAgent)

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


def test_procedures_embedded(cheshire_cat):
    # get embedded tools
    procedures, _ = cheshire_cat.memory.vectors.procedural.get_all_points()
    assert len(procedures) == 3

    for p in procedures:
        assert p.payload["metadata"]["source"] == "get_the_time"
        assert p.payload["metadata"]["type"] == "tool"
        trigger_type = p.payload["metadata"]["trigger_type"]
        content = p.payload["page_content"]
        assert trigger_type in ["start_example", "description"]

        if trigger_type == "start_example":
            assert content in ["what time is it", "get the time"]
        if trigger_type == "description":
            assert (
                content
                == "get_the_time: Useful to get the current time when asked. Input is always None."
            )

        # some check on the embedding
        assert isinstance(p.vector, list)
        expected_embed = cheshire_cat.embedder.embed_query(content)
        assert len(p.vector) == len(expected_embed)  # same embed
        # assert p.vector == expected_embed TODO: Qdrant does unwanted normalization
