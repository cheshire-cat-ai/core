import pytest
import asyncio
import time


from cat.mad_hatter.mad_hatter import MadHatter
from cat.agents.main_agent import MainAgent

from tests.agents.agent_fixtures import main_agent, stray

def test_main_agent_instantiation(main_agent):
    assert isinstance(main_agent, MainAgent)
    assert isinstance(
        main_agent.mad_hatter, MadHatter().__class__
    )  # damn singletons
    assert main_agent.verbose in [True, False]


@pytest.mark.asyncio  # to test async functions
async def test_execute_agent(main_agent, stray):
    # empty agent execution
    out = await main_agent.execute_agent(stray)
    assert out["input"] == "meow"
    assert out["episodic_memory"] == ""
    assert out["declarative_memory"] == ""
    assert out["tools_output"] == ""
    assert out["intermediate_steps"] == []
    assert (
        out["output"]
        == "AI: You did not configure a Language Model. Do it in the settings!"
    )
