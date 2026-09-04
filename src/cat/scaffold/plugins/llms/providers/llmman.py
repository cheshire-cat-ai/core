"""llmman — locally running models. No API key needed.

https://github.com/llmmanorg/llmman serves the Ollama API (alongside OpenAI- and
Anthropic-compatible ones) on port 17434; only the port differs from Ollama.
"""

import os

from pydantic import BaseModel, Field

from cat.base import OpenAICompatibleProvider


class LlmmanProvider(OpenAICompatibleProvider):
    """Locally running llmman models. No API key needed."""

    slug = "llmman"
    name = "llmman"
    description = "Locally running llmman models (OpenAI-compatible endpoint)."

    class Settings(BaseModel):
        base_url: str = Field(
            os.getenv("LLMMAN_URL", "http://localhost:17434/v1"), title="Base URL"
        )
        # llmman ignores the key but the OpenAI client requires a non-empty one,
        # so the unconfigured "No key set" path is never triggered.
        api_key: str = Field(os.getenv("LLMMAN_KEY", "llmman"), title="API Key")
