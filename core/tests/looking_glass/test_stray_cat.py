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
    assert isinstance(embedding[0], list)
    assert isinstance(embedding[0][0], float)


def test_stray_call(stray):
    msg = {"text": "Where do I go?", "user_id": "Alice"}

    reply = stray.loop.run_until_complete(stray.__call__(msg))

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
    stray.loop.run_until_complete(stray.__call__(msg))

    # recall after episodic memory was stored
    stray.recall_relevant_memories_to_working_memory(msg_text)

    assert stray.working_memory.recall_query == msg_text
    assert len(stray.working_memory.episodic_memories) == 1
    assert stray.working_memory.episodic_memories[0][0].page_content == msg_text


def test_stray_recall_invalid_collection_name(stray):
    with pytest.raises(ValueError) as exc_info:
        stray.recall("Hello, I'm Alice", "invalid_collection")
    assert "invalid_collection is not a valid collection" in str(exc_info.value)


def test_stray_recall_query_as_string(stray):
    msg_text = "Hello! I'm Alice"
    msg = {"text": msg_text, "user_id": "Alice"}

    # send message
    stray.loop.run_until_complete(stray.__call__(msg))

    memories = stray.recall("Alice", "episodic")

    assert len(memories) == 1
    assert memories[0][0].page_content == msg_text
    assert isinstance(memories[0][1], float)
    assert isinstance(memories[0][2], list)


def test_stray_recall_query_as_list_of_floats(stray):
    msg_text = "Hello! I'm Alice"
    msg = {"text": msg_text, "user_id": "Alice"}

    # send message
    stray.loop.run_until_complete(stray.__call__(msg))

    embedding = stray.embedder.embed_query(msg_text)
    memories = stray.recall(embedding, "episodic")

    assert len(memories) == 1
    assert memories[0][0].page_content == msg_text
    assert isinstance(memories[0][1], float)
    assert isinstance(memories[0][2], list)


def test_stray_recall_with_threshold(stray):
    msg_text = "Hello! I'm Alice"
    msg = {"text": msg_text, "user_id": "Alice"}

    # send message
    stray.loop.run_until_complete(stray.__call__(msg))

    memories = stray.recall("Alice", "episodic", threshold=1)
    assert len(memories) == 0


def test_stray_recall_all_memories(stray, client):
    expected_chunks = 4
    content_type = "application/pdf"
    file_name = "sample.pdf"
    file_path = f"tests/mocks/{file_name}"
    with open(file_path, "rb") as f:
        files = {"file": (file_name, f, content_type)}

        _ = client.post("/rabbithole/", files=files)

    memories = stray.recall("", "declarative", k=None)

    assert len(memories) == expected_chunks


def test_stray_recall_override_working_memory(stray):
    # empty working memory / episodic
    assert stray.working_memory.episodic_memories == []

    msg_text = "Hello! I'm Alice"
    msg = {"text": msg_text, "user_id": "Alice"}

    # send message
    stray.loop.run_until_complete(stray.__call__(msg))

    memories = stray.recall("Alice", "episodic", override_working_memory=True)
    assert stray.working_memory.episodic_memories == memories
    assert len(stray.working_memory.episodic_memories) == 1
    assert stray.working_memory.episodic_memories[0][0].page_content == msg_text


def test_stray_recall_by_metadata(stray, client):
    expected_chunks = 4
    content_type = "application/pdf"
    file_name = "sample.pdf"
    file_path = f"tests/mocks/{file_name}"
    with open(file_path, "rb") as f:
        files = {"file": (file_name, f, content_type)}

        _ = client.post("/rabbithole/", files=files)

    with open(file_path, "rb") as f:
        files = {"file": ("sample2.pdf", f, content_type)}

        _ = client.post("/rabbithole/", files=files)

    memories = stray.recall("late", "declarative", metadata={"source": "sample.pdf"})
    all_memories = stray.recall("", "declarative", k=None)

    assert len(all_memories) == expected_chunks * 2
    assert len(memories) == expected_chunks

    for memory in memories:
        assert memory[0].metadata["source"] == "sample.pdf"