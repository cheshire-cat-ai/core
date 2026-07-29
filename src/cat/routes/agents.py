from typing import List
from inspect import isclass

from ag_ui.core import RunAgentInput
from pydantic import BaseModel
from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import StreamingResponse

from cat.auth.depends import _get_user
from cat.ambient.runtime import ccat
from cat.types import Task, TaskResult
from cat.protocols.agui.adapter import AGUIInputError, run_agent_input_to_task
from cat.protocols.agui.streaming import AGUIStream


router = APIRouter(prefix="/agents", tags=["Agents"])
AgentMessageInput = RunAgentInput | Task


class AgentCard(BaseModel):
    slug: str
    name: str | None
    description: str | None
    plugin_id: str | None
    args_schema: dict | None = None


@router.get("")
async def list_agents(
    _=_get_user(),
) -> List[AgentCard]:
    """List all registered agents with full details."""

    agents = []
    for slug, Cls in ccat().registry.classes.get("agents", {}).items():
        args_schema = None
        ArgsSchema = getattr(Cls, 'ArgsSchema', None)
        if ArgsSchema is not None and isclass(ArgsSchema) and issubclass(ArgsSchema, BaseModel):
            args_schema = ArgsSchema.model_json_schema()

        agents.append(AgentCard(
            slug=slug,
            name=Cls.name or Cls.__name__,
            description=Cls.description,
            plugin_id=Cls.plugin_id,
            args_schema=args_schema,
        ))
    return agents


@router.post(
    "/{slug}/message",
    response_model=None,
    responses={
        200: {
            "model": TaskResult,
            "description": "AG-UI event stream or non-streaming Task result.",
            "content": {
                "text/event-stream": {
                    "schema": {"type": "string"},
                }
            },
        }
    },
)
async def agent_message(
    slug: str,
    input_data: AgentMessageInput = Body(
        ...,
        openapi_examples={
            "agui_stream": {
                "summary": "Streaming AG-UI message",
                "value": {
                    "threadId": "thread-123",
                    "runId": "run-456",
                    "state": {},
                    "messages": [
                        {
                            "id": "message-789",
                            "role": "user",
                            "content": "Meow!",
                        }
                    ],
                    "tools": [
                        {
                            "name": "confirm_action",
                            "description": "Ask for confirmation in the frontend.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "message": {"type": "string"},
                                },
                                "required": ["message"],
                            },
                        }
                    ],
                    "context": [],
                    "forwardedProps": {},
                },
            },
            "task_non_stream": {
                "summary": "Non-streaming Task message",
                "value": {
                    "messages": [
                        {
                            "role": "user",
                            "content": [{"type": "text", "text": "Hello!"}],
                        }
                    ],
                    "stream": False,
                },
            },
        },
    ),
    _=_get_user(),
) -> TaskResult | StreamingResponse:
    """Run an agent through AG-UI streaming or a non-streaming internal Task."""

    agent = await ccat().get("agents", slug, raise_error=False)
    if agent is None:
        raise HTTPException(status_code=404, detail=f"Agent '{slug}' not found.")

    if isinstance(input_data, RunAgentInput):
        try:
            task = run_agent_input_to_task(input_data)
        except AGUIInputError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        return AGUIStream(agent, task, input_data).stream()

    if input_data.stream:
        # Streaming is selected by the standard AG-UI payload, not by a
        # proprietary flag that native AG-UI clients do not send.
        raise HTTPException(
            status_code=422,
            detail="Streaming requests must use an AG-UI RunAgentInput payload.",
        )

    return await agent(input_data)
