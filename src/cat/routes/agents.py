from typing import List
from inspect import isclass

from pydantic import BaseModel
from fastapi import APIRouter, Body, Request, HTTPException

from cat.auth import get_user, get_ccat
from cat.types import Task, TaskResult
from cat.protocols.agui.streaming import AGUIStream


router = APIRouter(prefix="/agents", tags=["Agents"])

class AgentCard(BaseModel):
    slug: str
    name: str | None
    description: str | None
    plugin_id: str | None
    args_schema: dict | None = None


@router.get("")
async def list_agents(
    ccat=get_ccat(),
    _=get_user(),
) -> List[AgentCard]:
    """List all registered agents with full details."""

    agents = []
    for slug, Cls in ccat.factory.class_index.get("agents", {}).items():
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


@router.post("/{slug}/message")
async def agent_message(
    slug: str,
    http_request: Request,
    task: Task = Body(
        ...,
        openapi_examples={
            "simple": {
                "summary": "Simple text message",
                "value": {
                    "messages": [
                        {
                            "role": "user",
                            "content": [{"type": "text", "text": "Meow!"}]
                        }
                    ],
                    "stream": False,
                }
            },
            "with_args": {
                "summary": "Message with agent args",
                "value": {
                    "messages": [
                        {
                            "role": "user",
                            "content": [{"type": "text", "text": "Hello!"}]
                        }
                    ],
                    "args": {"temperature": 0.5},
                }
            }
        }
    ),
    _=get_user(),
    ccat=get_ccat(),
) -> TaskResult:
    """Send a message to a specific agent identified by its slug."""

    agent = await ccat.get(
        "agents",
        slug,
        request=http_request,
        raise_error=False
    )
    if agent is None:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{slug}' not found."
        )

    if task.stream:
        return AGUIStream(agent, task).stream()
    else:
        return await agent(task)
