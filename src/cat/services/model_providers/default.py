from typing import List, TYPE_CHECKING

from cat.services.model_providers.base import ModelProvider
from cat.types import Message, TextContent

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from cat.types import ToolCall
    from cat.mad_hatter.decorators import Tool


# Shown by the default LLM until a real provider is configured.
NOT_CONFIGURED_MESSAGE = (
    "No Language Model is configured yet. Choose one in the settings!"
)


class DefaultModelProvider(ModelProvider):
    """
    The "nothing configured yet" provider.

    It is the safe `default:default` fallback a fresh Cat boots with: it never
    needs a key, always lists a single `default` model, and answers every call
    with a clear next step instead of crashing. Selecting a real provider in the
    settings replaces it.
    """

    slug = "default"
    name = "Default (not configured)"
    description = "Placeholder until you configure a real model provider."

    async def list_llms(self) -> List[str]:
        return ["default"]

    async def list_embedders(self) -> List[str]:
        return ["default"]

    async def llm(
        self,
        model: str,
        messages: list["Message"],
        system_prompt: str = "",
        tools: list["Tool"] = [],
        on_token: "Callable[[str], Awaitable[None]] | None" = None,
        on_tool_call: "Callable[[ToolCall], Awaitable[None]] | None" = None,
    ) -> "Message":
        return Message(role="assistant", content=[TextContent(text=NOT_CONFIGURED_MESSAGE)])

    async def embed(self, model: str, text: str) -> list[float]:
        raise RuntimeError(NOT_CONFIGURED_MESSAGE)
