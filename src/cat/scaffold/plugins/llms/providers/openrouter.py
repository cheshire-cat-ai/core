"""OpenRouter — one key, hundreds of models, via the OpenAI-compatible endpoint."""

import os

from pydantic import BaseModel, Field

from cat.base import OpenAICompatibleProvider


class OpenRouterProvider(OpenAICompatibleProvider):
    """OpenRouter aggregator: many vendors behind one OpenAI-compatible API."""

    slug = "openrouter"
    name = "OpenRouter"
    description = "OpenRouter models."

    class Settings(BaseModel):
        base_url: str = Field("https://openrouter.ai/api/v1", title="Base URL")
        api_key: str = Field(os.getenv("OPENROUTER_KEY", ""), title="OpenRouter API Key")
