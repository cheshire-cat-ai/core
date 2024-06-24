
import pytest

from tests.agent_manager.agent_fixtures import agent_manager, stray

@pytest.mark.asyncio
async def test_execute_form_agent(agent_manager, stray):
    assert True  # TODO: this is going to be a mess
