"""Unit tests for MiniMax LLM provider integration."""

from unittest.mock import patch, MagicMock
from json import dumps
from fastapi.encoders import jsonable_encoder
from cat.factory.llm import (
    LLMMinimaxChatConfig,
    get_llms_schemas,
    get_llm_from_name,
)
from cat.factory.custom_llm import ChatMiniMax


# ------------------------------------------------------------------
# Unit tests – ChatMiniMax class
# ------------------------------------------------------------------

class TestChatMiniMaxClass:
    """Tests for the ChatMiniMax custom LangChain wrapper."""

    @patch("cat.factory.custom_llm.ChatOpenAI.__init__", return_value=None)
    def test_init_sets_base_url(self, mock_init):
        """ChatMiniMax should set openai_api_base to MiniMax endpoint."""
        ChatMiniMax(minimax_api_key="test-key", model_name="MiniMax-M2.7")
        _, kwargs = mock_init.call_args
        assert kwargs["openai_api_base"] == "https://api.minimax.io/v1"

    @patch("cat.factory.custom_llm.ChatOpenAI.__init__", return_value=None)
    def test_init_passes_api_key(self, mock_init):
        """API key should be forwarded as openai_api_key."""
        ChatMiniMax(minimax_api_key="sk-minimax-abc", model_name="MiniMax-M2.7")
        _, kwargs = mock_init.call_args
        assert kwargs["openai_api_key"] == "sk-minimax-abc"

    @patch("cat.factory.custom_llm.ChatOpenAI.__init__", return_value=None)
    def test_temperature_clamped_to_min(self, mock_init):
        """Temperature below 0.01 should be clamped to 0.01."""
        ChatMiniMax(minimax_api_key="k", model_name="MiniMax-M2.7", temperature=0.0)
        _, kwargs = mock_init.call_args
        assert kwargs["temperature"] == 0.01

    @patch("cat.factory.custom_llm.ChatOpenAI.__init__", return_value=None)
    def test_temperature_clamped_to_max(self, mock_init):
        """Temperature above 1.0 should be clamped to 1.0."""
        ChatMiniMax(minimax_api_key="k", model_name="MiniMax-M2.7", temperature=2.5)
        _, kwargs = mock_init.call_args
        assert kwargs["temperature"] == 1.0

    @patch("cat.factory.custom_llm.ChatOpenAI.__init__", return_value=None)
    def test_temperature_valid_passthrough(self, mock_init):
        """Valid temperature should pass through unchanged."""
        ChatMiniMax(minimax_api_key="k", model_name="MiniMax-M2.7", temperature=0.5)
        _, kwargs = mock_init.call_args
        assert kwargs["temperature"] == 0.5

    @patch("cat.factory.custom_llm.ChatOpenAI.__init__", return_value=None)
    def test_default_model_name(self, mock_init):
        """Default model_name should be MiniMax-M2.7."""
        ChatMiniMax(minimax_api_key="k")
        _, kwargs = mock_init.call_args
        assert kwargs["model_name"] == "MiniMax-M2.7"


# ------------------------------------------------------------------
# Unit tests – LLMMinimaxChatConfig factory class
# ------------------------------------------------------------------

class TestLLMMinimaxChatConfig:
    """Tests for the LLMMinimaxChatConfig Pydantic settings model."""

    def test_schema_has_human_readable_name(self):
        schema = LLMMinimaxChatConfig.model_json_schema()
        assert schema["humanReadableName"] == "MiniMax AI"

    def test_schema_has_description(self):
        schema = LLMMinimaxChatConfig.model_json_schema()
        assert "MiniMax" in schema["description"]

    def test_schema_has_link(self):
        schema = LLMMinimaxChatConfig.model_json_schema()
        assert "minimaxi.com" in schema["link"]

    def test_schema_requires_api_key(self):
        schema = LLMMinimaxChatConfig.model_json_schema()
        assert "minimax_api_key" in schema["required"]

    def test_default_model_name(self):
        schema = LLMMinimaxChatConfig.model_json_schema()
        props = schema["properties"]
        assert props["model_name"]["default"] == "MiniMax-M2.7"

    def test_default_temperature(self):
        schema = LLMMinimaxChatConfig.model_json_schema()
        props = schema["properties"]
        assert props["temperature"]["default"] == 0.7


# ------------------------------------------------------------------
# Unit tests – Factory registration
# ------------------------------------------------------------------

class TestMinimaxFactoryRegistration:
    """Ensure MiniMax is properly registered in the LLM factory."""

    def test_minimax_in_allowed_schemas(self, client):
        schemas = get_llms_schemas()
        assert "LLMMinimaxChatConfig" in schemas

    def test_get_llm_from_name_returns_minimax(self, client):
        cls = get_llm_from_name("LLMMinimaxChatConfig")
        assert cls is LLMMinimaxChatConfig

    def test_minimax_appears_in_settings_endpoint(self, client):
        response = client.get("/llm/settings")
        json = response.json()
        assert response.status_code == 200
        names = [s["name"] for s in json["settings"]]
        assert "LLMMinimaxChatConfig" in names

    def test_get_minimax_setting_by_name(self, client):
        response = client.get("/llm/settings/LLMMinimaxChatConfig")
        json = response.json()
        assert response.status_code == 200
        assert json["name"] == "LLMMinimaxChatConfig"
        assert json["schema"]["languageModelName"] == "LLMMinimaxChatConfig"

    def test_upsert_minimax_setting(self, client):
        """Saving MiniMax config triggers LLM + embedder reload which calls
        the real API. With a fake key the reload fails and the route rolls back.
        We verify the PUT endpoint validates the payload and returns 400
        (invalid key) rather than 422 (schema validation error)."""
        payload = {
            "minimax_api_key": "test-key-123",
            "model_name": "MiniMax-M2.5",
            "temperature": 0.5,
        }
        response = client.put("/llm/settings/LLMMinimaxChatConfig", json=payload)
        # 400 = schema valid, API key invalid during reload (expected in tests)
        # 200 = would mean the API key happened to work (not expected here)
        assert response.status_code in (200, 400)
