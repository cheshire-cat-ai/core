"""
Named vendor presets for the most common LLM endpoints.

Each preset is just an `OpenAICompatibleProvider` (imported from core) with a
known `base_url` baked in, so the user only has to supply an API key — or
nothing at all, for keyless local servers. Every vendor here exposes an
OpenAI-compatible endpoint, so there is no custom wire-format code and this
plugin adds **no Python dependencies** beyond the `openai` SDK already in core.

There are deliberately no hardcoded model lists: model names are free text the
user provides, and live ones are discovered via `list_llms()` once a key is set.
Anything that needs a native, non-OpenAI wire format ships as its own plugin.
"""

from typing import List

from pydantic import BaseModel, Field

from cat.base import OpenAICompatibleProvider
from cat import log


class OpenAIProvider(OpenAICompatibleProvider):
    """OpenAI models (GPT, o-series, embeddings)."""

    slug = "openai"
    name = "OpenAI"
    description = "OpenAI models via the official API."

    class Settings(BaseModel):
        base_url: str = Field("https://api.openai.com/v1", title="Base URL")
        api_key: str = Field("", title="OpenAI API Key")


class AnthropicProvider(OpenAICompatibleProvider):
    """Anthropic Claude models via the OpenAI-compatible endpoint."""

    slug = "anthropic"
    name = "Anthropic"
    description = "Anthropic Claude models (OpenAI-compatible endpoint)."

    class Settings(BaseModel):
        base_url: str = Field("https://api.anthropic.com/v1/", title="Base URL")
        api_key: str = Field("", title="Anthropic API Key")

    async def _fetch_models(self) -> List[str]:
        """Override discovery to use Anthropic's *native* /v1/models endpoint.

        Anthropic's OpenAI-compatibility layer only covers /v1/chat/completions.
        GET /v1/models is the native endpoint: it authenticates with
        `x-api-key` + `anthropic-version`, and rejects the OpenAI SDK's
        `Authorization: Bearer` with a 401 "Invalid bearer token" — so
        `client.models.list()` can never work here, valid key or not. Query it
        directly with the headers Anthropic expects.
        """
        import httpx

        if not self.settings.api_key:
            return []
        url = self.settings.base_url.rstrip("/") + "/models"
        try:
            async with httpx.AsyncClient(timeout=self.DISCOVERY_TIMEOUT_S) as client:
                resp = await client.get(
                    url,
                    headers={
                        "x-api-key": self.settings.api_key,
                        "anthropic-version": "2023-06-01",
                    },
                )
                resp.raise_for_status()
                return [m["id"] for m in resp.json().get("data", [])]
        except Exception as e:
            log.warning(f"{self.slug}: could not fetch model list ({e}); skipping autocomplete.")
            return []


class GeminiProvider(OpenAICompatibleProvider):
    """Google Gemini models via the OpenAI-compatible endpoint."""

    slug = "gemini"
    name = "Google Gemini"
    description = "Google Gemini models (OpenAI-compatible endpoint)."

    class Settings(BaseModel):
        base_url: str = Field(
            "https://generativelanguage.googleapis.com/v1beta/openai/", title="Base URL"
        )
        api_key: str = Field("", title="Gemini API Key")


class OllamaProvider(OpenAICompatibleProvider):
    """Locally running Ollama models. No API key needed."""

    slug = "ollama"
    name = "Ollama"
    description = "Locally running Ollama models (OpenAI-compatible endpoint)."

    class Settings(BaseModel):
        base_url: str = Field("http://localhost:11434/v1", title="Base URL")
        # Ollama ignores the key but the OpenAI client requires a non-empty one,
        # so the unconfigured "No key set" path is never triggered.
        api_key: str = Field("ollama", title="API Key")


class VLLMProvider(OpenAICompatibleProvider):
    """Self-hosted vLLM server. Serves whatever model you launched it with."""

    slug = "vllm"
    name = "vLLM"
    description = "Self-hosted vLLM server (OpenAI-compatible endpoint)."

    class Settings(BaseModel):
        base_url: str = Field("http://localhost:8000/v1", title="Base URL")
        # vLLM ignores the key but the OpenAI client requires a non-empty one.
        api_key: str = Field("EMPTY", title="API Key")
