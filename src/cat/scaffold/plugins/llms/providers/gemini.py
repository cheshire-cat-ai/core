"""Google Gemini — models via the OpenAI-compatible endpoint."""

import os

from pydantic import BaseModel, Field

from cat.base import OpenAICompatibleProvider


class GeminiProvider(OpenAICompatibleProvider):
    """Google Gemini models via the OpenAI-compatible endpoint."""

    slug = "gemini"
    name = "Google Gemini"
    description = "Google Gemini models (OpenAI-compatible endpoint)."

    base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"

    class Settings(BaseModel):
        api_key: str = Field(os.getenv("GEMINI_KEY", ""), title="Gemini API Key")
