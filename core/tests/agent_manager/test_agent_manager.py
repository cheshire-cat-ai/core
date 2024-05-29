import pytest
import asyncio
import time

from langchain.docstore.document import Document

from cat.looking_glass.cheshire_cat import CheshireCat
from cat.looking_glass.stray_cat import StrayCat
from cat.mad_hatter.mad_hatter import MadHatter
from cat.looking_glass.agent_manager import AgentManager


@pytest.fixture
def agent_manager(client):
    yield CheshireCat().agent_manager # each test receives as argument the agent_manager instance

@pytest.fixture
def stray(client):

    user_id = "Alice"
    stray_cat = StrayCat(user_id=user_id, main_loop=asyncio.new_event_loop())
    stray_cat.working_memory.user_message_json = {
        "user_id": user_id,
        "text": "meow"
    }
    yield stray_cat


def test_agent_manager_instantiation(agent_manager):

    assert isinstance(agent_manager, AgentManager)
    assert isinstance(agent_manager.mad_hatter, MadHatter().__class__) # damn singletons
    assert agent_manager.verbose in [True, False]


@pytest.mark.asyncio # to test async functions
async def test_execute_agent(agent_manager, stray):
    
    # empty agent execution
    out = await agent_manager.execute_agent(stray)
    assert out["input"] == "meow"
    assert out["episodic_memory"] == ""
    assert out["declarative_memory"] == ""
    assert out["tools_output"] == ""
    assert out["intermediate_steps"] == []
    assert out["output"] == "AI: You did not configure a Language Model. Do it in the settings!"


def test_format_agent_input(agent_manager, stray):

    # empty agent execution
    agent_input = agent_manager.format_agent_input(stray)
    assert agent_input["input"] == "meow"
    assert agent_input["episodic_memory"] == ""
    assert agent_input["declarative_memory"] == ""
    assert agent_input["tools_output"] == ""

    # episodic and declarative memories are present
    stray = fill_working_memory(stray)
    agent_input = agent_manager.format_agent_input(stray)
    assert agent_input["input"] == "meow"
    assert agent_input["episodic_memory"] == \
"""## Context of things the Human said in the past: 
  - A (0 minutes ago)
  - B (1 days ago)"""
    assert agent_input["declarative_memory"] == \
"""## Context of documents containing relevant information: 
  - A (extracted from a.pdf)
  - B (extracted from http://b)"""
    assert agent_input["tools_output"] == ""


def test_agent_prompt_episodic_memories(agent_manager, stray):

    # empty episodic memory
    episodic_prompt = agent_manager.agent_prompt_episodic_memories([])
    assert episodic_prompt == ""

    # some points in episodic memory
    stray = fill_working_memory(stray)

    episodic_prompt = agent_manager.agent_prompt_episodic_memories(
        stray.working_memory.episodic_memories
    )
    assert episodic_prompt == \
"""## Context of things the Human said in the past: 
  - A (0 minutes ago)
  - B (1 days ago)"""
    

def test_agent_prompt_declarative_memories(agent_manager, stray):

    # empty declarative memory
    declarative_prompt = agent_manager.agent_prompt_declarative_memories([])
    assert declarative_prompt == ""

    # some points in declarative memory
    stray = fill_working_memory(stray) 
    declarative_prompt = agent_manager.agent_prompt_declarative_memories(
        stray.working_memory.declarative_memories
    )
    assert declarative_prompt == \
"""## Context of documents containing relevant information: 
  - A (extracted from a.pdf)
  - B (extracted from http://b)"""
    

@pytest.mark.asyncio
async def test_execute_form_agent(agent_manager, stray):

    assert True # TODO: this is going to be a mess


@pytest.mark.asyncio
async def test_execute_procedures_agent(agent_manager, stray):

    assert True # TODO: this is going to be a mess


@pytest.mark.asyncio
async def test_execute_memory_chain(agent_manager, stray):

    assert True # TODO: this is going to be a mess


# utility to add content to the working memory
def fill_working_memory(stray_cat):

    stray_cat.working_memory.episodic_memories = [
        [
            Document(
                page_content="A",
                metadata={
                    "when": time.time(),
                }
            ),
            0.99
        ],
        [
            Document(
                page_content="B",
                metadata={
                    "when": time.time() - (60 * 60 * 24),
                }
            ),
            0.88
        ]
    ]

    stray_cat.working_memory.declarative_memories = [
        [
            Document(
                page_content="A",
                metadata={
                    "source": "a.pdf",
                }
            ),
            0.99
        ],
        [
            Document(
                page_content="B",
                metadata={
                    "source": "http://b",
                }
            ),
            0.88
        ]
    ]

    stray_cat.working_memory.procedural_memories = [
        [
            Document(
                page_content="what time is it",
                metadata={
                    "source": "TODO",
                }
            ),
            0.99
        ]
    ]

    return stray_cat
