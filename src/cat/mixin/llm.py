import time
from uuid import uuid4
from typing import Dict, List, TYPE_CHECKING

from cat.protocols.agui import events
from cat import log

if TYPE_CHECKING:
    from cat.types import Message
    from cat.mad_hatter.decorators import Tool


class LLMMixin:
    """Mixin for LLM and client streaming methods."""

    async def send_json(self, data: Dict):
        """Send JSON data to the client via stream callback."""
        if hasattr(self.request.state, "stream_callback"):
            await self.request.state.stream_callback(data)

    async def agui_event(self, event: events.BaseEvent):
        """Send an AGUI event to the client."""
        await self.send_json(dict(event))

    async def llm(
        self,
        system_prompt: str,
        model: str | None = None,
        messages: list["Message"] = [],
        tools: list["Tool"] = [],
        stream: bool = True,
    ) -> "Message":
        """Generate a response using the Large Language Model."""

        if model:
            slug = model
        elif self.model:
            slug = self.model
        else:
            core_settings = await self.ccat.get("config", "core")
            slug = (await core_settings.load_settings()).default_llm

        # Parse "provider:model" slug
        if ":" in slug:
            provider_slug, model_slug = slug.split(":", 1)
        else:
            provider_slug, model_slug = "default", slug

        provider = await self.ccat.get(
            "model_providers", provider_slug, raise_error=True
        )

        # Build on_token callback for streaming AGUI events
        on_token = None
        text_started = False
        if stream:
            async def on_token(token: str):
                nonlocal text_started
                if token:
                    if not text_started:
                        await self.agui_event(
                            events.TextMessageStartEvent(
                                message_id=str(uuid4()),
                                timestamp=int(time.time())
                            )
                        )
                        text_started = True
                    await self.agui_event(
                        events.TextMessageContentEvent(
                            message_id=str(uuid4()),
                            delta=token,
                            timestamp=int(time.time())
                        )
                    )

        result = await provider.llm(
            model_slug, messages, system_prompt, tools, on_token
        )

        if text_started:
            await self.agui_event(
                events.TextMessageEndEvent(
                    message_id=str(uuid4()),
                    timestamp=int(time.time())
                )
            )

        return result
