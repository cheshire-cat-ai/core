import pytest

from cat.agents.main_agent import MainAgent
from cat.agents import AgentOutput


@pytest.mark.asyncio
async def test_execute_main_agent(stray):
    
    main_agent = MainAgent(stray)
    
    # empty agent execution
    out = await main_agent.execute()
    assert isinstance(out, AgentOutput)
    assert not out.return_direct
    assert out.intermediate_steps == []
    assert "You did not configure" in out.output
