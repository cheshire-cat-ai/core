from typing import List, TYPE_CHECKING
from pydantic import BaseModel, Field, PrivateAttr

from .messages import Message
from cat.protocols.model_context.type_wrappers import Resource

if TYPE_CHECKING:
    from cat.mad_hatter.decorators import Tool


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

    # Client tools are runtime-only data populated by the AG-UI adapter. Keeping
    # them private prevents ordinary Task JSON from selecting client execution.
    _client_tools: List["Tool"] = PrivateAttr(default_factory=list)


class TaskResult(Task):
    """
    Output from an Agent.

    Deliberately the same shape as `Task`: what an agent returns is what the next
    agent can be handed, so a result feeds straight back in with no adapter. The
    distinct name marks direction (in vs out), not a different set of fields.
    """

    pass
