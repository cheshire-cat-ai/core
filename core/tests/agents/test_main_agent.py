import pytest


from cat.mad_hatter.mad_hatter import MadHatter
from cat.agents.main_agent import MainAgent
from cat.agents import AgentOutput


def test_main_agent_instantiation(main_agent):
    assert isinstance(main_agent, MainAgent)
    assert isinstance(
        main_agent.mad_hatter, MadHatter().__class__
    )  # damn singletons
    assert main_agent.verbose in [True, False]


@pytest.mark.asyncio  # to test async functions
async def test_execute_main_agent(main_agent, stray):
    # empty agent execution
    out = main_agent.execute(stray)
    assert isinstance(out, AgentOutput)
    assert not out.return_direct
    assert out.intermediate_steps == []
    assert out.output == \
        "AI: You did not configure a Language Model. Do it in the settings!"
