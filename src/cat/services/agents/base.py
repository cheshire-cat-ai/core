from typing import List, TYPE_CHECKING
from inspect import isclass

from pydantic import BaseModel

from cat.types import Message, Task, TaskResult
from cat.mad_hatter.decorators import Tool
from cat.services.service import Service
from cat.capabilities import llm, agui_event
from cat import log

if TYPE_CHECKING:
    from cat.base import Directive


class Agent(Service):
    """
    An agent is a *verb you run*: a fresh, non-singleton instance per run that
    holds its execution state as instance attributes (`task`, `result`,
    `system_prompt`, `tools`) and is thrown away afterwards. Because every run
    uses a new instance, mutating that state is safe under concurrency.

    Ambient needs come from imports (`from cat import user, llm, hook`), never
    from a `self.ccat`/`self.request` back-reference.
    """

    service_type = "agents"
    singleton = False

    system_prompt = "You are an Agent in the Cheshire Cat AI fleet. Help the user and other agents with their requests."
    model = None  # a slug like "openai:gpt-4o"; if None, taken from core settings

    directives: List["Directive"] = []

    args: BaseModel | None = None

    async def __call__(self, task: Task) -> TaskResult:
        """
        Main entry point: run the agent like a function. Sets up run state,
        fires lifecycle hooks, and runs the agentic loop.
        """

        self._validate_args(task)

        async with self.mcp_clients.get_user_client(self) as mcp_client:
            self.mcp = mcp_client

            # Per-run state on a fresh instance.
            self.task = task
            self.result = TaskResult()
            self.system_prompt = await self.get_system_prompt()
            self.tools = await self.list_tools()

            self.task = await self.execute_hook(
                "before_agent_execution", self.task
            )
            self.task = await self.execute_hook(
                f"before_{self.slug}_agent_execution", self.task
            )

            await self.start()
            await self.loop()
            await self.finish()

            self.result = await self.execute_hook(
                f"after_{self.slug}_agent_execution", self.result
            )
            self.result = await self.execute_hook(
                "after_agent_execution", self.result
            )

        return self.result

    async def start(self):
        """Called before the agentic loop. Runs directive start phase."""
        for d in self.directives:
            await d.start(self)

    async def finish(self):
        """Called after the agentic loop. Runs directive finish phase."""
        for d in self.directives:
            await d.finish(self)

    async def loop(self):
        """
        Agentic loop.
        Runs LLM generations and tool calls until the LLM stops generating tool calls.
        Updates chat response in place.
        """

        # snapshot system prompt to be reset before each step (good old RAG use cases)
        _base_prompt = self.system_prompt

        while True:

            # reset system prompt to baseline
            self.system_prompt = _base_prompt

            # let directives work on the agent
            for d in self.directives:
                await d.step(self)

            llm_mex: Message = await llm(
                self.system_prompt,
                model=self.model,
                messages=self.task.messages + self.result.messages,
                tools=self.tools,
                stream=self.task.stream,
            )

            self.result.messages.append(llm_mex)
            log.convo_summary(
                self.system_prompt,
                self.task.messages + self.result.messages,
                self.slug
            )

            if len(llm_mex.tool_calls) == 0:
                # No tool calls, exit the loop
                return
            else:
                # LLM has chosen to use tools, run them
                for tool_call in llm_mex.tool_calls:
                    tool_message = await self.call_tool(tool_call)
                    self.result.messages.append(tool_message)

    async def get_system_prompt(self) -> str:
        """
        Build the system prompt.
        Base method delegates prompt construction to hooks.
        Prompt is built in two parts: prefix and suffix.
        Prefix is the main prompt, suffix can be used to append extra instructions and context (i.e. RAG).
        Override for custom behavior.
        """

        prompt = type(self).system_prompt

        prompt = await self.execute_hook(
            "agent_prompt_prefix",
            prompt
        )
        prompt = await self.execute_hook(
            f"agent_{self.slug}_prompt_prefix",
            prompt
        )
        prompt_suffix = await self.execute_hook(
            "agent_prompt_suffix", ""
        )
        prompt_suffix = await self.execute_hook(
            f"agent_{self.slug}_prompt_suffix",
            prompt_suffix
        )

        return prompt + prompt_suffix

    async def list_tools(self) -> List[Tool]:
        """Get plugins' tools, MCP tools, and agent's own tools in CatTool format."""

        # Get MCP tools
        mcp_tools = await self.mcp.list_tools()
        mcp_tools = [
            Tool.from_fastmcp(t, self.mcp.call_tool)
            for t in mcp_tools
        ]

        # Get agent's own internal tools
        agent_tools = self.instantiate_agent_tools()

        # Combine all tools
        from cat.context import app
        tools = await self.execute_hook(
            "agent_allowed_tools",
            mcp_tools + app().mad_hatter.tools + agent_tools
        )

        return tools

    async def call_tool(self, tool_call, *args, **kwargs):
        """Call a tool."""

        name = tool_call.name
        for t in self.tools:
            if t.name == name:
                return await t.execute(self, tool_call)

        raise Exception(f"Tool {name} not found")

    async def call_agent(self, slug, task: Task) -> TaskResult:
        """Run another agent by slug. No request threading required."""
        from cat.capabilities import call_agent
        return await call_agent(slug, task)

    async def agui_event(self, event):
        """Emit an AGUI event to the current client (sourced from request context)."""
        await agui_event(event)

    def _validate_args(self, task: Task) -> None:
        """Validate and inject ArgsSchema from task."""
        ArgsSchema = getattr(self.__class__, 'ArgsSchema', None)
        if ArgsSchema is not None and isclass(ArgsSchema) and issubclass(ArgsSchema, BaseModel):
            self.args = ArgsSchema.model_validate(task.args)

    def instantiate_agent_tools(self) -> List[Tool]:
        """Find Tool instances on class and bind them to the agent instance."""
        return [
            attr.bind_to(self)
            for name in dir(self.__class__)
            if isinstance(attr := getattr(self.__class__, name, None), Tool)
        ]
