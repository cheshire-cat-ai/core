"""Unit tests for MiniMax Embedder integration."""

from unittest.mock import patch, MagicMock
import json
from cat.factory.embedder import (
    EmbedderMinimaxConfig,
    get_embedders_schemas,
    get_embedder_from_name,
)
from cat.factory.custom_embedder import MiniMaxEmbeddings


# ------------------------------------------------------------------
# Unit tests – MiniMaxEmbeddings class
# ------------------------------------------------------------------

class TestMiniMaxEmbeddingsClass:
    """Tests for the MiniMaxEmbeddings custom embedder."""

    def test_init_sets_url(self):
        emb = MiniMaxEmbeddings(minimax_api_key="key")
        assert emb.url == "https://api.minimax.io/v1/embeddings"

    def test_init_default_model(self):
        emb = MiniMaxEmbeddings(minimax_api_key="key")
        assert emb.model == "embo-01"

    def test_init_default_embed_type(self):
        emb = MiniMaxEmbeddings(minimax_api_key="key")
        assert emb.embed_type == "db"

    @patch("cat.factory.custom_embedder.httpx.post")
    def test_embed_documents_sends_db_type(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "vectors": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
            "base_resp": {"status_code": 0, "status_msg": "success"},
        }
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp

        emb = MiniMaxEmbeddings(minimax_api_key="test-key")
        result = emb.embed_documents(["hello", "world"])

        assert result == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]

        call_kwargs = mock_post.call_args
        sent_data = json.loads(call_kwargs.kwargs.get("data") or call_kwargs[1].get("data"))
        assert sent_data["type"] == "db"
        assert sent_data["model"] == "embo-01"
        assert sent_data["texts"] == ["hello", "world"]

    @patch("cat.factory.custom_embedder.httpx.post")
    def test_embed_query_sends_query_type(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "vectors": [[0.1, 0.2, 0.3]],
            "base_resp": {"status_code": 0, "status_msg": "success"},
        }
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp

        emb = MiniMaxEmbeddings(minimax_api_key="test-key")
        result = emb.embed_query("hello")

        assert result == [0.1, 0.2, 0.3]

        call_kwargs = mock_post.call_args
        sent_data = json.loads(call_kwargs.kwargs.get("data") or call_kwargs[1].get("data"))
        assert sent_data["type"] == "query"

    @patch("cat.factory.custom_embedder.httpx.post")
    def test_embed_sends_auth_header(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"vectors": [[0.1]], "base_resp": {"status_code": 0}}
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp

        emb = MiniMaxEmbeddings(minimax_api_key="sk-minimax-xyz")
        emb.embed_query("test")

        call_kwargs = mock_post.call_args
        headers = call_kwargs.kwargs.get("headers") or call_kwargs[1].get("headers")
        assert headers["Authorization"] == "Bearer sk-minimax-xyz"


# ------------------------------------------------------------------
# Unit tests – EmbedderMinimaxConfig factory class
# ------------------------------------------------------------------

class TestEmbedderMinimaxConfig:
    """Tests for the EmbedderMinimaxConfig settings model."""

    def test_schema_human_readable_name(self):
        schema = EmbedderMinimaxConfig.model_json_schema()
        assert schema["humanReadableName"] == "MiniMax Embedder"

    def test_schema_requires_api_key(self):
        schema = EmbedderMinimaxConfig.model_json_schema()
        assert "minimax_api_key" in schema["required"]

    def test_default_model(self):
        schema = EmbedderMinimaxConfig.model_json_schema()
        assert schema["properties"]["model"]["default"] == "embo-01"


# ------------------------------------------------------------------
# Unit tests – Factory registration
# ------------------------------------------------------------------

class TestMinimaxEmbedderRegistration:
    """Ensure MiniMax embedder is registered in the factory."""

    def test_minimax_in_embedder_schemas(self, client):
        schemas = get_embedders_schemas()
        assert "EmbedderMinimaxConfig" in schemas

    def test_get_embedder_from_name(self, client):
        cls = get_embedder_from_name("EmbedderMinimaxConfig")
        assert cls is EmbedderMinimaxConfig

    def test_minimax_in_embedder_settings_endpoint(self, client):
        response = client.get("/embedder/settings")
        json_resp = response.json()
        assert response.status_code == 200
        names = [s["name"] for s in json_resp["settings"]]
        assert "EmbedderMinimaxConfig" in names
