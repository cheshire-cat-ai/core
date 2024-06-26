
import pytest
import asyncio

from cat.looking_glass.cheshire_cat import CheshireCat
from cat.looking_glass.stray_cat import StrayCat

# fixtures to test AgnetManager class

@pytest.fixture
def main_agent(client):
    yield CheshireCat().main_agent  # each test receives as argument the main agent instance


@pytest.fixture
def stray(client):
    user_id = "Alice"
    stray_cat = StrayCat(user_id=user_id, main_loop=asyncio.new_event_loop())
    stray_cat.working_memory.user_message_json = {"user_id": user_id, "text": "meow"}
    yield stray_cat