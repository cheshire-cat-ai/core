from typing import List, TYPE_CHECKING
from collections.abc import Awaitable, Callable

from cat.base import ModelProvider
from cat.types import Message, TextContent, ToolCall

if TYPE_CHECKING:
    from cat.mad_hatter.decorators import Tool


class MockModelProvider(ModelProvider):
    """Mock model provider for testing."""

    slug = "mock"
    description = "Mock model provider for testing."

    responses: List[str] = ["I'm a fake LLM!"]
    _call_count: int = 0

    async def setup(self):
        pass

    async def list_llms(self) -> List[str]:
        return ["mock"]

    async def llm(
        self,
        model: str,
        messages: list[Message],
        system_prompt: str = "",
        tools: list["Tool"] = [],
        on_token: Callable[[str], Awaitable[None]] | None = None,
        on_tool_call: Callable[[ToolCall], Awaitable[None]] | None = None,
    ) -> Message:
        text = self.responses[self._call_count % len(self.responses)]
        self._call_count += 1

        if on_token:
            for word in text.split(" "):
                await on_token(word + " ")

        return Message(
            role="assistant",
            content=[TextContent(text=text)]
        )
