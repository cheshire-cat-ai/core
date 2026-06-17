import asyncio
import json
import time
from asyncio import Queue
from uuid import uuid4
from typing import AsyncGenerator, Any, TYPE_CHECKING

from fastapi.responses import StreamingResponse
from cat.protocols.agui import events
from cat import log

if TYPE_CHECKING:
    from cat import Agent
    from cat.types import Task


class AgentStream:
    """
    Base class for streaming agent execution.
    Handles queue, callback setup, and agent execution.
    Subclasses override lifecycle hooks and formatting.
    """

    media_type: str = "text/event-stream"  # Default for SSE, override in subclasses

    def __init__(self, agent: "Agent", task: "Task"):
        self.agent = agent
        self.task = task
        self.queue = Queue()

    async def _before_run(self) -> AsyncGenerator[Any, None]:
        """Override to emit events before agent runs."""
        return
        yield  # Make this a generator

    async def _after_run(self, result: Any) -> AsyncGenerator[Any, None]:
        """Override to emit events after agent completes successfully."""
        return
        yield  # Make this a generator

    async def _on_error(self, error: Exception) -> AsyncGenerator[Any, None]:
        """Override to emit events when an error occurs."""
        return
        yield  # Make this a generator

    async def _event_generator(self) -> AsyncGenerator[str, None]:
        """
        Override to format events for your protocol.
        Base implementation raises NotImplementedError.
        """
        raise NotImplementedError("Subclasses must implement _event_generator()")
        yield  # Make this a generator

    def stream(self) -> StreamingResponse:
        """
        Return a StreamingResponse ready to be returned from FastAPI endpoint.
        All protocol implementations use this same method.
        """
        return StreamingResponse(
            self._event_generator(),
            media_type=self.media_type
        )

    async def _stream_events(self) -> AsyncGenerator[Any, None]:
        """
        Base streaming logic: lifecycle hooks, callback setup, agent execution.
        Yields raw event objects from subclass hooks and agent callbacks.
        """
        # Emit before-run events
        async for event in self._before_run():
            yield event

        # Setup callback to populate queue
        self.agent.request.state.stream_callback = lambda event: asyncio.create_task(
            self.queue.put(event)
        )

        async def runner() -> None:
            try:
                # Run the agent
                result = await self.agent(self.task)

                # Emit after-run events
                async for event in self._after_run(result):
                    await self.queue.put(event)

            except Exception as e:
                # Agent execution error - emit error events
                async for event in self._on_error(e):
                    await self.queue.put(event)
                log.error(e)

            finally:
                await self.queue.put(None)  # Signal completion

        # Run agent concurrently
        runner_task = asyncio.create_task(runner())

        try:
            # Yield events from queue as they arrive
            while True:
                msg = await self.queue.get()
                if msg is None:
                    break
                yield msg

            await runner_task  # Ensure completion

        finally:
            # Cancel runner if streaming is interrupted (e.g., client disconnect)
            if not runner_task.done():
                runner_task.cancel()
                try:
                    await runner_task
                except asyncio.CancelledError:
                    pass


class AGUIStream(AgentStream):
    """
    AGUI protocol streaming implementation.
    Adds AGUI lifecycle events and formats as Server-Sent Events (SSE).
    """

    def __init__(self, agent: "Agent", task: "Task"):
        super().__init__(agent, task)
        self.run_id = str(uuid4())
        self.thread_id = "_"  # TODOV2: should come from request/session

    async def _before_run(self) -> AsyncGenerator[Any, None]:
        """Emit RunStartedEvent before agent execution."""
        yield events.RunStartedEvent(
            timestamp=int(time.time()),
            thread_id=self.thread_id,
            run_id=self.run_id
        )

    async def _after_run(self, result: Any) -> AsyncGenerator[Any, None]:
        """Emit RunFinishedEvent after successful agent execution."""
        yield events.RunFinishedEvent(
            timestamp=int(time.time()),
            thread_id=self.thread_id,
            run_id=self.run_id,
            result=result.model_dump()
        )

    async def _on_error(self, error: Exception) -> AsyncGenerator[Any, None]:
        """Emit RunErrorEvent when an error occurs."""
        yield events.RunErrorEvent(
            timestamp=int(time.time()),
            message=str(error)
        )

    async def _event_generator(self) -> AsyncGenerator[str, None]:
        """
        Generate SSE formatted events.
        Yields formatted SSE messages for AGUI clients.
        """
        async for event in self._stream_events():
            yield f"data: {json.dumps(dict(event))}\n\n"
