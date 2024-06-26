import pytest
import asyncio
import time


from cat.mad_hatter.mad_hatter import MadHatter
from cat.agents.agent_manager import AgentManager

from tests.agent_manager.agent_fixtures import agent_manager, stray

def test_agent_manager_instantiation(agent_manager):
    assert isinstance(agent_manager, AgentManager)
    assert isinstance(
        agent_manager.mad_hatter, MadHatter().__class__
    )  # damn singletons
    assert agent_manager.verbose in [True, False]


@pytest.mark.asyncio  # to test async functions
async def test_execute_agent(agent_manager, stray):
    # empty agent execution
    out = await agent_manager.execute_agent(stray)
    assert out["input"] == "meow"
    assert out["episodic_memory"] == ""
    assert out["declarative_memory"] == ""
    assert out["tools_output"] == ""
    assert out["intermediate_steps"] == []
    assert (
        out["output"]
        == "AI: You did not configure a Language Model. Do it in the settings!"
    )
