import random
from typing import List, TYPE_CHECKING
from collections.abc import Awaitable, Callable

from .base import ModelProvider
from ...types import Message, TextContent, ToolCall

if TYPE_CHECKING:
    from cat.mad_hatter.decorators import Tool


class DefaultModelProvider(ModelProvider):
    """Default model provider (placeholder models)."""

    slug = "default"
    name = "Default model provider"
    description = "Default model provider with placeholder models."

    async def setup(self):
        pass

    async def list_llms(self) -> List[str]:
        return ["default"]

    async def list_embedders(self) -> List[str]:
        return ["default"]

    async def llm(
        self,
        model: str,
        messages: list[Message],
        system_prompt: str = "",
        tools: list["Tool"] = [],
        on_token: Callable[[str], Awaitable[None]] | None = None,
        on_tool_call: Callable[[ToolCall], Awaitable[None]] | None = None,
    ) -> Message:
        text = "You did not configure a Language Model. Do it in the settings!"
        return Message(
            role="assistant",
            content=[TextContent(text=text)]
        )

    async def embed(self, model: str, text: str) -> list[float]:
        return [random.random() for _ in range(8)]
