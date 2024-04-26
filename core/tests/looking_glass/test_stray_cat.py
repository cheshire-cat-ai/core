import pytest
import asyncio

from cat.looking_glass.stray_cat import StrayCat
from cat.memory.working_memory import WorkingMemory


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
        "user_message_json": {
            "text": "WHO... R... U..."
        }
    }

    reply = stray.loop.run_until_complete(
        stray.__call__(msg)
    )

    assert reply == 0
