"""Integration tests for MiniMax LLM provider.

These tests call the real MiniMax API and require:
  - MINIMAX_API_KEY environment variable to be set

Skip with: pytest -m "not integration"
"""

import os
import pytest

pytestmark = pytest.mark.skipif(
    not os.environ.get("MINIMAX_API_KEY"),
    reason="MINIMAX_API_KEY not set – skipping MiniMax integration tests",
)


class TestMiniMaxLLMIntegration:
    """Integration tests hitting the real MiniMax chat API."""

    def test_chat_completion(self):
        from cat.factory.custom_llm import ChatMiniMax

        llm = ChatMiniMax(
            minimax_api_key=os.environ["MINIMAX_API_KEY"],
            model_name="MiniMax-M2.5-highspeed",
            temperature=0.01,
            streaming=False,
        )
        response = llm.invoke("Say exactly: hello world")
        text = response.content if hasattr(response, "content") else str(response)
        assert len(text) > 0

    def test_chat_streaming(self):
        from cat.factory.custom_llm import ChatMiniMax

        llm = ChatMiniMax(
            minimax_api_key=os.environ["MINIMAX_API_KEY"],
            model_name="MiniMax-M2.5-highspeed",
            temperature=0.01,
            streaming=True,
        )
        chunks = list(llm.stream("Say exactly: integration test"))
        assert len(chunks) > 0

    def test_factory_instantiation(self):
        from cat.factory.llm import LLMMinimaxChatConfig

        llm = LLMMinimaxChatConfig.get_llm_from_config(
            {
                "minimax_api_key": os.environ["MINIMAX_API_KEY"],
                "model_name": "MiniMax-M2.5-highspeed",
                "temperature": 0.5,
            }
        )
        response = llm.invoke("Reply with one word: ok")
        text = response.content if hasattr(response, "content") else str(response)
        assert len(text) > 0
