"""Ollama — locally running models. No API key needed."""

import os

from pydantic import BaseModel, Field

from cat.base import OpenAICompatibleProvider


class OllamaProvider(OpenAICompatibleProvider):
    """Locally running Ollama models. No API key needed."""

    slug = "ollama"
    name = "Ollama"
    description = "Locally running Ollama models (OpenAI-compatible endpoint)."

    class Settings(BaseModel):
        base_url: str = Field(
            os.getenv("OLLAMA_URL", "http://localhost:11434/v1"), title="Base URL"
        )
        # Ollama ignores the key but the OpenAI client requires a non-empty one,
        # so the unconfigured "No key set" path is never triggered.
        api_key: str = Field(os.getenv("OLLAMA_KEY", "ollama"), title="API Key")
