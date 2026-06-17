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


# Returned by `llm()` when the provider has no API key configured, instead of
# raising. Keeps a fresh, unconfigured Cat responsive with a clear next step.
NO_KEY_MESSAGE = "No key set. Update it into the settings"


class OpenAICompatibleProvider(ModelProvider):
    """
    A model provider speaking the OpenAI wire format.

    This is the default provider and the shared engine for most others: any
    endpoint that exposes an OpenAI-compatible API (OpenAI, Anthropic, Gemini,
    Ollama, vLLM, LM Studio, OpenRouter, …) works by pointing `base_url` at it
    and setting `api_key`. Vendor-specific providers subclass this and only
    change the default `base_url` (and a curated model list); all message/tool
    conversion, streaming and embedding logic lives here.
    """

    service_type = "model_providers"

    slug = "openai_compatible"
    name = "OpenAI-compatible"
    description = "Any OpenAI-compatible API. Set base_url and api_key."

    class Settings(BaseModel):
        base_url: str = Field(
            default="https://api.openai.com/v1",
            title="Base URL",
            description="OpenAI-compatible endpoint (e.g. http://localhost:11434/v1).",
        )
        api_key: str = Field(
            default="",
            title="API Key",
            description="API key for the endpoint. Leave empty for keyless local servers.",
        )

    async def setup(self):
        from openai import AsyncOpenAI

        api_key = self.settings.api_key
        if not api_key:
            # No key: stay unconfigured. `llm()` returns NO_KEY_MESSAGE.
            self.client = None
            return
        self.client = AsyncOpenAI(base_url=self.settings.base_url, api_key=api_key)

    # -- model discovery ----------------------------------------------------

    # Short timeout for model discovery only: this runs on the settings page,
    # so a misconfigured or offline endpoint must fail fast instead of blocking
    # the UI. Real llm()/embed() calls keep the client's default (generous) timeout.
    DISCOVERY_TIMEOUT_S = 3.0

    async def _fetch_models(self) -> List[str]:
        """Fetch all model IDs from the vendor API. Returns [] on failure."""
        if not getattr(self, "client", None):
            return []
        try:
            models = await self.client.with_options(timeout=self.DISCOVERY_TIMEOUT_S).models.list()
            return [m.id for m in models.data]
        except Exception as e:
            log.warning(f"{self.slug}: could not fetch model list ({e}); skipping autocomplete.")
            return []

    def _is_embedder(self, model_id: str) -> bool:
        """Return True if model_id is an embedder. Override for custom filtering."""
        return "embed" in model_id

    def _is_llm(self, model_id: str) -> bool:
        """Return True if model_id is a chat/LLM model. Override for custom filtering."""
        return not self._is_embedder(model_id)

    async def list_llms(self) -> List[str]:
        """Live LLM model ids from the endpoint. Empty until a key is set.

        Optional discovery for a UI autocomplete — never a hard constraint on
        what model can be used. The model is always a free-text string.
        """
        return [m for m in await self._fetch_models() if self._is_llm(m)]

    async def list_embedders(self) -> List[str]:
        """Live embedder model ids from the endpoint. Empty until a key is set."""
        return [m for m in await self._fetch_models() if self._is_embedder(m)]

    # -- format conversion (public, overridable) ----------------------------

    async def build_messages(self, messages: list["Message"], system_prompt: str) -> list[dict]:
        """Convert Cat messages to OpenAI message format."""
        result = []
        if system_prompt:
            result.append({"role": "system", "content": system_prompt})
        for msg in messages:
            result.append(await self.convert_message(msg))
        return result

    async def convert_message(self, msg: "Message") -> dict:
        """Convert a single Cat Message to OpenAI format."""
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

        # user or plain assistant message
        content = []
        for block in msg.content:
            if isinstance(block, TextContent):
                content.append({"type": "text", "text": block.text})
            elif isinstance(block, ImageContent):
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:{block.mimeType};base64,{block.data}"},
                })

        # Flatten to string if only one text block
        if len(content) == 1 and content[0]["type"] == "text":
            return {"role": msg.role, "content": content[0]["text"]}
        return {"role": msg.role, "content": content}

    def build_tools(self, tools: list["Tool"]) -> list[dict]:
        """Convert Cat tools to OpenAI tool format."""
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

    def parse_response(self, response) -> "Message":
        """Convert OpenAI response to Cat Message."""
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

    async def stream_completion(
        self,
        model: str,
        messages: list[dict],
        tools: list[dict],
        on_token: "Callable[[str], Awaitable[None]]",
        on_tool_call: "Callable[[ToolCall], Awaitable[None]] | None" = None,
    ) -> "Message":
        """Stream completion and return complete Message."""
        from cat.types import Message

        kwargs = {"model": model, "messages": messages}
        if tools:
            kwargs["tools"] = tools

        full_text = ""
        tool_calls_acc: dict[int, dict] = {}

        stream = await self.client.chat.completions.create(stream=True, **kwargs)
        async for event in stream:
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

        # Unconfigured: answer with a clear next step instead of crashing.
        if not getattr(self, "client", None):
            return Message(role="assistant", content=[TextContent(text=NO_KEY_MESSAGE)])

        oai_messages = await self.build_messages(messages, system_prompt)
        oai_tools = self.build_tools(tools) if tools else []

        if on_token:
            return await self.stream_completion(model, oai_messages, oai_tools, on_token, on_tool_call)

        kwargs = {"model": model, "messages": oai_messages}
        if oai_tools:
            kwargs["tools"] = oai_tools

        response = await self.client.chat.completions.create(**kwargs)
        result = self.parse_response(response)

        if on_tool_call:
            for tc in result.tool_calls:
                await on_tool_call(tc)

        return result

    async def embed(self, model: str, text: str) -> list[float]:
        """Embed text using the OpenAI embeddings API."""
        if not getattr(self, "client", None):
            raise RuntimeError(NO_KEY_MESSAGE)
        response = await self.client.embeddings.create(model=model, input=text)
        return response.data[0].embedding
