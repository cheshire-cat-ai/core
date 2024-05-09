import pytest
import asyncio

from cat.looking_glass.stray_cat import StrayCat
from cat.memory.working_memory import WorkingMemory
from cat.convo.messages import MessageWhy, CatMessage


@pytest.fixture
def stray(client):
    yield StrayCat(user_id="Alice", main_loop=asyncio.new_event_loop())


def test_stray_initialization(stray):

    assert isinstance(stray, StrayCat)
    assert stray.user_id == "Alice"
    assert isinstance(stray.working_memory, WorkingMemory)


def test_stray_nlp(stray):

    res = stray.llm("hey")
    assert "You did not configure" in res

    embedding = stray.embedder.embed_documents(["hey"])
    assert type(embedding[0]) == list
    assert type(embedding[0][0]) == float


def test_stray_call(stray):

    msg = {
        "text": "Where do I go?",
        "user_id": "Alice"
    }

    reply = stray.loop.run_until_complete(
        stray.__call__(msg)
    )

    assert type(reply) == CatMessage
    assert "You did not configure" in reply.content
    assert reply.user_id == "Alice"
    assert reply.type == "chat"
    assert type(reply.why) == MessageWhy


# TODO: update these tests once we have a real LLM in tests
def test_stray_classify(stray):
    
    label = stray.classify("I feel good", labels=["positive", "negative"])
    assert label == None # TODO: should be "positive"

    label = stray.classify("I feel bad", labels={"positive": ["I'm happy"], "negative": ["I'm sad"]})
    assert label == None # TODO: should be "negative"


def test_recall_to_working_memory(stray):

    # empty working memory / episodic
    assert stray.working_memory.episodic_memories == []
    
    msg_text = "Where do I go?"
    msg = {
        "text": msg_text,
        "user_id": "Alice"
    }
    
    # send message
    stray.loop.run_until_complete(
        stray.__call__(msg)
    )

    # recall after episodic memory was stored
    stray.recall_relevant_memories_to_working_memory(msg_text)

    assert stray.working_memory.recall_query == msg_text
    assert len(stray.working_memory.episodic_memories) == 1
    assert stray.working_memory.episodic_memories[0][0].page_content == msg_text