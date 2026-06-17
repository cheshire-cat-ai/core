"""
LiteLLM AI gateway provider.

Uses the LiteLLM SDK to route requests to 100+ LLM providers (OpenAI,
Anthropic, Bedrock, Vertex AI, Groq, Mistral, Cohere, etc.) through a
single unified interface. No separate proxy server required -- just
``pip install litellm``, set the provider's API key as an env var, and
use the LiteLLM model string (e.g. ``anthropic/claude-sonnet-4-6``).

Unlike the ``OpenAI-compatible`` provider which needs a running proxy,
this plugin calls providers natively via their SDKs, with automatic
parameter translation and ``drop_params=True`` for cross-provider compat.
"""

import json
from typing import List, TYPE_CHECKING

from pydantic import BaseModel, Field

from cat.services.model_providers.base import ModelProvider
from cat.protocols.model_context.type_wrappers import TextContent, ImageContent, ToolCall
from cat import log

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from cat.types import Message
    from cat.mad_hatter.decorators import Tool


NO_KEY_MESSAGE = (
    "No API key configured for LiteLLM. Set the provider's API key as an "
    "environment variable (e.g. ANTHROPIC_API_KEY, OPENAI_API_KEY) or enter "
    "it in the settings below."
)


class LiteLLMProvider(ModelProvider):
    """
    LiteLLM AI gateway -- 100+ providers through one interface.

    Model names follow LiteLLM's ``provider/model`` format:
    ``anthropic/claude-sonnet-4-6``, ``bedrock/anthropic.claude-3-haiku``,
    ``vertex_ai/gemini-2.0-flash``, ``groq/llama-3.3-70b``, etc.

    Provider API keys are read from environment variables by default
    (ANTHROPIC_API_KEY, OPENAI_API_KEY, etc.). An optional api_key in
    settings is forwarded to every call for single-key setups.
    """

    service_type = "model_providers"

    slug = "litellm"
    name = "LiteLLM"
    description = "100+ LLM providers via LiteLLM AI gateway (Anthropic, Bedrock, Vertex, Groq, etc.)."

    class Settings(BaseModel):
        api_key: str = Field(
            default="",
            title="API Key",
            description=(
                "Optional. Forwarded to every LiteLLM call. Leave empty to "
                "use provider-specific env vars (ANTHROPIC_API_KEY, etc.)."
            ),
        )

    async def setup(self):
        try:
            import litellm  # noqa: F401
            self._available = True
        except ImportError:
            log.warning(
                "litellm package not installed. Install with: "
                "pip install 'litellm>=1.80,<1.87'"
            )
            self._available = False

    async def list_llms(self) -> List[str]:
        if not getattr(self, "_available", False):
            return []
        try:
            import litellm
            return list(litellm.model_list)
        except Exception as e:
            log.warning(f"litellm: could not fetch model list ({e})")
            return []

    async def list_embedders(self) -> List[str]:
        return []

    # -- format conversion (same as OpenAICompatibleProvider) ------------------

    async def build_messages(self, messages: list["Message"], system_prompt: str) -> list[dict]:
        result = []
        if system_prompt:
            result.append({"role": "system", "content": system_prompt})
        for msg in messages:
            result.append(await self._convert_message(msg))
        return result

    async def _convert_message(self, msg: "Message") -> dict:
        if msg.role == "tool":
            return {
                "role": "tool",
                "tool_call_id": msg.tool_call_id,
                "content": msg.text,
            }

        if msg.role == "assistant" and msg.tool_calls:
            return {
                "role": "assistant",
                "content": msg.text or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.name,
                            "arguments": json.dumps(tc.args),
                        },
                    }
                    for tc in msg.tool_calls
                ],
            }

        content = []
        for block in msg.content:
            if isinstance(block, TextContent):
                content.append({"type": "text", "text": block.text})
            elif isinstance(block, ImageContent):
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:{block.mimeType};base64,{block.data}"},
                })

        if len(content) == 1 and content[0]["type"] == "text":
            return {"role": msg.role, "content": content[0]["text"]}
        return {"role": msg.role, "content": content}

    def _build_tools(self, tools: list["Tool"]) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.input_schema,
                },
            }
            for tool in tools
        ]

    def _parse_response(self, response) -> "Message":
        from cat.types import Message

        choice = response.choices[0]
        oai_msg = choice.message

        text = oai_msg.content or ""
        tool_calls = []

        if oai_msg.tool_calls:
            for tc in oai_msg.tool_calls:
                tool_calls.append(ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    args=json.loads(tc.function.arguments),
                ))

        content = [TextContent(type="text", text=text)] if text else []
        return Message(
            role="assistant",
            content=content,
            tool_calls=tool_calls,
        )

    def _api_kwargs(self) -> dict:
        """Common kwargs for every litellm call."""
        kwargs = {"drop_params": True}
        api_key = getattr(self.settings, "api_key", "")
        if api_key:
            kwargs["api_key"] = api_key
        return kwargs

    # -- completion ------------------------------------------------------------

    async def llm(
        self,
        model: str,
        messages: list["Message"],
        system_prompt: str = "",
        tools: list["Tool"] = [],
        on_token: "Callable[[str], Awaitable[None]] | None" = None,
        on_tool_call: "Callable[[ToolCall], Awaitable[None]] | None" = None,
    ) -> "Message":
        from cat.types import Message

        if not getattr(self, "_available", False):
            return Message(role="assistant", content=[TextContent(text=NO_KEY_MESSAGE)])

        import litellm

        oai_messages = await self.build_messages(messages, system_prompt)
        oai_tools = self._build_tools(tools) if tools else []

        kwargs = {"model": model, "messages": oai_messages, **self._api_kwargs()}
        if oai_tools:
            kwargs["tools"] = oai_tools

        if on_token:
            return await self._stream_completion(kwargs, on_token, on_tool_call)

        response = await litellm.acompletion(**kwargs)
        result = self._parse_response(response)

        if on_tool_call:
            for tc in result.tool_calls:
                await on_tool_call(tc)

        return result

    async def _stream_completion(
        self,
        kwargs: dict,
        on_token: "Callable[[str], Awaitable[None]]",
        on_tool_call: "Callable[[ToolCall], Awaitable[None]] | None" = None,
    ) -> "Message":
        from cat.types import Message
        import litellm

        full_text = ""
        tool_calls_acc: dict[int, dict] = {}

        response = await litellm.acompletion(stream=True, **kwargs)
        async for event in response:
            if not event.choices:
                continue
            delta = event.choices[0].delta
            if delta.content:
                full_text += delta.content
                await on_token(delta.content)
            if delta.tool_calls:
                for tc_delta in delta.tool_calls:
                    idx = tc_delta.index
                    if idx not in tool_calls_acc:
                        tool_calls_acc[idx] = {"id": "", "name": "", "args_str": ""}
                    if tc_delta.id:
                        tool_calls_acc[idx]["id"] = tc_delta.id
                    if tc_delta.function:
                        if tc_delta.function.name:
                            tool_calls_acc[idx]["name"] = tc_delta.function.name
                        if tc_delta.function.arguments:
                            tool_calls_acc[idx]["args_str"] += tc_delta.function.arguments

        tool_calls = [
            ToolCall(id=tc["id"], name=tc["name"], args=json.loads(tc["args_str"] or "{}"))
            for tc in tool_calls_acc.values()
        ]

        if on_tool_call:
            for tc in tool_calls:
                await on_tool_call(tc)

        content = [TextContent(type="text", text=full_text)] if full_text else []
        return Message(
            role="assistant",
            content=content,
            tool_calls=tool_calls,
        )

    # -- embeddings ------------------------------------------------------------

    async def embed(self, model: str, text: str) -> list[float]:
        if not getattr(self, "_available", False):
            raise RuntimeError(
                "litellm package not installed. "
                "Install with: pip install 'litellm>=1.80,<1.87'"
            )

        import litellm

        response = await litellm.aembedding(
            model=model, input=text, **self._api_kwargs()
        )
        return response.data[0]["embedding"]
