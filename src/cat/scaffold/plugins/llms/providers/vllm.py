"""vLLM — self-hosted server. Serves whatever model you launched it with."""

import os

from pydantic import BaseModel, Field

from cat.base import OpenAICompatibleProvider


class VLLMProvider(OpenAICompatibleProvider):
    """Self-hosted vLLM server. Serves whatever model you launched it with."""

    slug = "vllm"
    name = "vLLM"
    description = "Self-hosted vLLM server (OpenAI-compatible endpoint)."

    class Settings(BaseModel):
        base_url: str = Field(
            os.getenv("VLLM_URL", "http://localhost:8000/v1"), title="Base URL"
        )
        # vLLM ignores the key but the OpenAI client requires a non-empty one.
        api_key: str = Field(os.getenv("VLLM_KEY", "EMPTY"), title="API Key")
