from typing import List, TYPE_CHECKING
from abc import abstractmethod

from cat.services.service import Service

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from cat.types import Message, ToolCall
    from cat.mad_hatter.decorators import Tool


class ModelProvider(Service):
    """
    Base class to expose deep learning models.

    ModelProviders are singleton services that make LLM and embedding
    calls directly.
    """

    service_type = "model_providers"

    async def setup(self):
        """
        Setup the vendor (e.g. load API keys from settings).

        Override this method to load configuration (API keys, hosts, etc.).
        """
        pass

    async def list_llms(self) -> List[str]:
        """
        Return a list of available LLM slugs (without provider prefix).

        Example: ["gpt-4", "gpt-3.5-turbo"]

        Override this in subclasses.
        """
        return []

    async def list_embedders(self) -> List[str]:
        """
        Return a list of available embedder slugs (without provider prefix).

        Example: ["text-embedding-3-small", "text-embedding-ada-002"]

        Override this in subclasses.
        """
        return []

    @abstractmethod
    async def llm(
        self,
        model: str,
        messages: list["Message"],
        system_prompt: str = "",
        tools: list["Tool"] = [],
        on_token: "Callable[[str], Awaitable[None]] | None" = None,
        on_tool_call: "Callable[[ToolCall], Awaitable[None]] | None" = None,
    ) -> "Message":
        """
        Chat completion.

        Parameters
        ----------
        model : str
            Model identifier (e.g. "gpt-4", "llama3").
        messages : list[Message]
            Conversation history (user, assistant, tool messages).
        system_prompt : str
            System instructions.
        tools : list[Tool]
            Available tools. Each has .name, .description, .input_schema.
        on_token : callback
            If provided, enables streaming. Called with each text delta
            as it arrives.
        on_tool_call : callback
            If provided, called with each complete ToolCall as it is
            parsed from the stream (or from the final response).

        Returns
        -------
        Message
            Complete assistant Message with role="assistant",
            content=[TextContent(...)], and optionally
            tool_calls=[{"id": ..., "name": ..., "args": {...}}, ...]
        """
        pass

    async def embed(self, model: str, text: str) -> list[float]:
        """
        Embed a single text string.

        Parameters
        ----------
        text : str
            The text to embed.
        model : str
            Model identifier (e.g. "text-embedding-3-small").

        Returns
        -------
        list[float] | None
            The embedding vector, or None if not supported.

        Override this in subclasses to implement embedding.
        """
        return [0.0]
