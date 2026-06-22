"""OpenAI — GPT, o-series and embedding models via the official API."""

import os

from pydantic import BaseModel, Field

from cat.base import OpenAICompatibleProvider


class OpenAIProvider(OpenAICompatibleProvider):
    """OpenAI models (GPT, o-series, embeddings)."""

    slug = "openai"
    name = "OpenAI"
    description = "OpenAI models via the official API."

    base_url = "https://api.openai.com/v1"

    class Settings(BaseModel):
        api_key: str = Field(os.getenv("OPENAI_KEY", ""), title="OpenAI API Key")
