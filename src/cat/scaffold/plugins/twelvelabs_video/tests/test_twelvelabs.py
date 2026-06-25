"""TwelveLabs plugin suite.

Lives in the plugin, so the harness auto-includes it (core + this plugin) for
every test here. Two no-network tests assert the agent and its tool register
correctly and that the missing-key path is handled gracefully; one live test
runs Pegasus end to end and is skipped unless TWELVELABS_API_KEY is set.
"""

import os

import pytest
import pytest_asyncio

from cat.ambient.runtime import ccat


@pytest_asyncio.fixture(scope="function")
async def cheshire_cat(async_client):
    yield ccat()


def _analyze_video_tool(agent):
    """The agent's bound analyze_video tool (its `.func` is the callable)."""
    return next(
        t.func for t in agent.instantiate_agent_tools() if t.name == "analyze_video"
    )


async def test_agent_registered_with_tool(cheshire_cat):
    """The plugin's agent loads by slug and exposes the analyze_video tool."""
    agent = await cheshire_cat.get("agents", "twelvelabs")
    assert agent.name == "TwelveLabs Video Agent"
    tool_names = {t.name for t in agent.instantiate_agent_tools()}
    assert "analyze_video" in tool_names


async def test_missing_key_returns_clear_message(cheshire_cat, monkeypatch):
    """With no API key set, the tool returns guidance instead of raising."""
    monkeypatch.delenv("TWELVELABS_API_KEY", raising=False)
    agent = await cheshire_cat.get("agents", "twelvelabs")
    analyze = _analyze_video_tool(agent)
    result = await analyze(video_url="https://example.com/v.mp4", prompt="?")
    assert "TWELVELABS_API_KEY" in result


@pytest.mark.skipif(
    not os.getenv("TWELVELABS_API_KEY"),
    reason="TWELVELABS_API_KEY not set — skipping live Pegasus call.",
)
async def test_analyze_video_live(cheshire_cat):
    """Live: Pegasus watches a short public sample video and answers."""
    agent = await cheshire_cat.get("agents", "twelvelabs")
    analyze = _analyze_video_tool(agent)
    result = await analyze(
        video_url="https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/360/Big_Buck_Bunny_360_10s_1MB.mp4",
        prompt="In one sentence, what happens in this video?",
    )
    assert isinstance(result, str) and len(result) > 0
    assert not result.startswith("TwelveLabs analysis failed")
