"""Anthropic — Claude models via the OpenAI-compatible endpoint."""

import os
from typing import List

from pydantic import BaseModel, Field

from cat.base import OpenAICompatibleProvider
from cat import log


class AnthropicProvider(OpenAICompatibleProvider):
    """Anthropic Claude models via the OpenAI-compatible endpoint."""

    slug = "anthropic"
    name = "Anthropic"
    description = "Anthropic Claude models (OpenAI-compatible endpoint)."

    base_url = "https://api.anthropic.com/v1/"

    class Settings(BaseModel):
        api_key: str = Field(os.getenv("ANTHROPIC_KEY", ""), title="Anthropic API Key")

    async def fetch_models(self) -> List[str]:
        """Override discovery to use Anthropic's *native* /v1/models endpoint.

        Anthropic's OpenAI-compatibility layer only covers /v1/chat/completions.
        GET /v1/models is the native endpoint: it authenticates with
        `x-api-key` + `anthropic-version`, and rejects the OpenAI SDK's
        `Authorization: Bearer` with a 401 "Invalid bearer token" — so
        `client.models.list()` can never work here, valid key or not. Query it
        directly with the headers Anthropic expects.
        """
        import httpx

        s = await self.load_settings()
        if not s.api_key:
            return []
        url = self.resolve_base_url(s).rstrip("/") + "/models"
        try:
            async with httpx.AsyncClient(timeout=self.DISCOVERY_TIMEOUT_S) as client:
                resp = await client.get(
                    url,
                    headers={
                        "x-api-key": s.api_key,
                        "anthropic-version": "2023-06-01",
                    },
                )
                resp.raise_for_status()
                return [m["id"] for m in resp.json().get("data", [])]
        except Exception as e:
            log.warning(f"{self.slug}: could not fetch model list ({e}); skipping autocomplete.")
            return []
