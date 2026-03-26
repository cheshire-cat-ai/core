"""Integration tests for MiniMax LLM + Embedder provider.

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


class TestMiniMaxEmbedderIntegration:
    """Integration tests hitting the real MiniMax embeddings API."""

    def test_embed_query(self):
        from cat.factory.custom_embedder import MiniMaxEmbeddings

        emb = MiniMaxEmbeddings(minimax_api_key=os.environ["MINIMAX_API_KEY"])
        vec = emb.embed_query("hello world")
        assert isinstance(vec, list)
        assert len(vec) == 1536  # embo-01 produces 1536-dim vectors

    def test_embed_documents(self):
        from cat.factory.custom_embedder import MiniMaxEmbeddings

        emb = MiniMaxEmbeddings(minimax_api_key=os.environ["MINIMAX_API_KEY"])
        vecs = emb.embed_documents(["hello", "world"])
        assert len(vecs) == 2
        assert all(len(v) == 1536 for v in vecs)

    def test_factory_instantiation(self):
        from cat.factory.embedder import EmbedderMinimaxConfig

        emb = EmbedderMinimaxConfig.get_embedder_from_config(
            {
                "minimax_api_key": os.environ["MINIMAX_API_KEY"],
                "model": "embo-01",
            }
        )
        vec = emb.embed_query("test embedding")
        assert isinstance(vec, list)
        assert len(vec) == 1536
