
from __future__ import annotations
from typing import TYPE_CHECKING

from ..service import RequestService

if TYPE_CHECKING:
    from cat.services.agents.base import Agent


class Directive(RequestService):
    """Base class for a Directive, to inspect and change the Agent before generation."""

    service_type = "directives"

    async def start(self, agent: Agent) -> None:
        """Called once before the agentic loop begins. Use for permanent setup (filter tools, adjust base prompt).

        Parameters
        ----------
        agent : Agent
            The agent instance to modify in place.
        """
        pass

    async def step(self, agent: Agent) -> None:
        """Called each iteration of the agentic loop, after prompt reset. Use for per-iteration context (RAG, guardrails).

        Parameters
        ----------
        agent : Agent
            The agent instance to modify in place.
        """
        pass

    async def finish(self, agent: Agent) -> None:
        """Called once after the agentic loop ends. Use for post-processing (save memories, log).

        Parameters
        ----------
        agent : Agent
            The agent instance to modify in place.
        """
        pass
