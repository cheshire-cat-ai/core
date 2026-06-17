from typing import List
from pydantic import BaseModel, Field

from .messages import Message
from cat.protocols.model_context.type_wrappers import Resource


class Task(BaseModel):
    """
    Input for agents.
    Agents receive a Task and return a TaskResult.
    Contains messages (conversation) and resources (context/data).
    """

    messages: List[Message] = Field(
        default_factory=list,
        description="List of messages for the agent."
    )

    resources: List[Resource] = Field(
        default_factory=list,
        description="List of resources (documents, context, data)"
    )

    args: dict = Field(
        default_factory=dict,
        description="Runtime parameters for the agent. Validated against the agent's ArgsSchema when defined."
    )

    stream: bool = Field(
        True,
        description="Whether to enable streaming tokens or not."
    )

class TaskResult(Task):
    """
    Output from an Agent.
    """

    pass
    #status: Literal[]
