import pytest
import time

from langchain.docstore.document import Document

from tests.agent_manager.agent_fixtures import agent_manager, stray


def test_format_agent_input_on_empty_memory(agent_manager, stray):
    # empty memory
    agent_input = agent_manager.format_agent_input(stray)
    assert agent_input["input"] == "meow"
    assert agent_input["episodic_memory"] == ""
    assert agent_input["declarative_memory"] == ""
    assert agent_input["tools_output"] == ""


def test_format_agent_input(agent_manager, stray):

    # episodic and declarative memories are present
    stray = fill_working_memory(stray)

    agent_input = agent_manager.format_agent_input(stray)
    assert agent_input["input"] == "meow"
    assert (
        agent_input["episodic_memory"]
        == """## Context of things the Human said in the past: 
  - A (0 minutes ago)
  - B (1 days ago)"""
    )
    assert (
        agent_input["declarative_memory"]
        == """## Context of documents containing relevant information: 
  - A (extracted from a.pdf)
  - B (extracted from http://b)"""
    )
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
    assert (
        episodic_prompt
        == """## Context of things the Human said in the past: 
  - A (0 minutes ago)
  - B (1 days ago)"""
    )


def test_agent_prompt_declarative_memories(agent_manager, stray):
    # empty declarative memory
    declarative_prompt = agent_manager.agent_prompt_declarative_memories([])
    assert declarative_prompt == ""

    # some points in declarative memory
    stray = fill_working_memory(stray)
    declarative_prompt = agent_manager.agent_prompt_declarative_memories(
        stray.working_memory.declarative_memories
    )
    assert (
        declarative_prompt
        == """## Context of documents containing relevant information: 
  - A (extracted from a.pdf)
  - B (extracted from http://b)"""
    )

# utility to add content to the working memory
def fill_working_memory(stray_cat):
    stray_cat.working_memory.episodic_memories = [
        [
            Document(
                page_content="A",
                metadata={
                    "when": time.time(),
                },
            ),
            0.99,
        ],
        [
            Document(
                page_content="B",
                metadata={
                    "when": time.time() - (60 * 60 * 24),
                },
            ),
            0.88,
        ],
    ]

    stray_cat.working_memory.declarative_memories = [
        [
            Document(
                page_content="A",
                metadata={
                    "source": "a.pdf",
                },
            ),
            0.99,
        ],
        [
            Document(
                page_content="B",
                metadata={
                    "source": "http://b",
                },
            ),
            0.88,
        ],
    ]

    stray_cat.working_memory.procedural_memories = [
        [
            Document(
                page_content="what time is it",
                metadata={
                    "source": "TODO",
                },
            ),
            0.99,
        ]
    ]

    return stray_cat
