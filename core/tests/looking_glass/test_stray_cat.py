import pytest
import asyncio

from cat.looking_glass.stray_cat import StrayCat
from cat.memory.working_memory import WorkingMemory
from cat.convo.messages import MessageWhy, CatMessage
from cat.mad_hatter.decorators.hook import CatHook

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
    assert isinstance(embedding[0], list)
    assert isinstance(embedding[0][0], float)


def test_stray_call(stray):
    msg = {"text": "Where do I go?", "user_id": "Alice"}

    reply = stray.__call__(msg)

    assert isinstance(reply, CatMessage)
    assert "You did not configure" in reply.content
    assert reply.user_id == "Alice"
    assert reply.type == "chat"
    assert isinstance(reply.why, MessageWhy)


# TODO: update these tests once we have a real LLM in tests
def test_stray_classify(stray):
    label = stray.classify("I feel good", labels=["positive", "negative"])
    assert label is None  # TODO: should be "positive"

    label = stray.classify(
        "I feel bad", labels={"positive": ["I'm happy"], "negative": ["I'm sad"]}
    )
    assert label is None  # TODO: should be "negative"


def test_recall_to_working_memory(stray):
    # empty working memory / episodic
    assert stray.working_memory.episodic_memories == []

    msg_text = "Where do I go?"
    msg = {"text": msg_text, "user_id": "Alice"}

    # send message
    stray.__call__(msg)

    # recall after episodic memory was stored
    stray.recall_relevant_memories_to_working_memory(msg_text)

    assert stray.working_memory.recall_query == msg_text
    assert len(stray.working_memory.episodic_memories) == 1
    assert stray.working_memory.episodic_memories[0][0].page_content == msg_text


# TODO: should we gather all tests regarding hooks in a folder?
def test_stray_fast_reply_hook(stray):
    user_msg = "hello"
    fast_reply_msg = "This is a fast reply"

    def fast_reply_hook(fast_reply: dict, cat):
        if user_msg in cat.working_memory.user_message_json.text:
            fast_reply["output"] = fast_reply_msg
            return fast_reply

    fast_reply_hook = CatHook(name="fast_reply", func=fast_reply_hook, priority=0)
    fast_reply_hook.plugin_id = "fast_reply_hook"
    stray.mad_hatter.hooks["fast_reply"] = [fast_reply_hook]

    msg = {"text": user_msg, "user_id": "Alice"}

    # send message
    res = stray.__call__(msg)

    assert isinstance(res, CatMessage)
    assert res.content == fast_reply_msg

    # there should be NO side effects
    assert stray.working_memory.user_message_json.text == user_msg
    assert len(stray.working_memory.history) == 0
    stray.recall_relevant_memories_to_working_memory(user_msg)
    assert len(stray.working_memory.episodic_memories) == 0
