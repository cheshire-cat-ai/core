"""OpenRouter — one key, hundreds of models, via the OpenAI-compatible endpoint."""

import os

from pydantic import BaseModel, Field

from cat.base import OpenAICompatibleProvider


class OpenRouterProvider(OpenAICompatibleProvider):
    """OpenRouter aggregator: many vendors behind one OpenAI-compatible API."""

    slug = "openrouter"
    name = "OpenRouter"
    description = "OpenRouter models."

    base_url = "https://openrouter.ai/api/v1"

    class Settings(BaseModel):
        api_key: str = Field(os.getenv("OPENROUTER_KEY", ""), title="OpenRouter API Key")
