from typing import List, TYPE_CHECKING
from inspect import isclass

from pydantic import BaseModel

from cat.types import Message, Task, TaskResult, TextContent
from cat.mad_hatter.decorators import Tool
from cat.services.service import Service
from cat.ambient import llm, execute_hook
from cat import log

if TYPE_CHECKING:
    from cat.base import Directive


class Agent(Service):
    """
    Holds execution state as instance attributes (`task`, `result`,
    `system_prompt`, `tools`) and is thrown away afterwards. Because every run
    uses a new instance, mutating state is safe under concurrency.

    Ambient needs come from imports (`from cat import user, llm, hook`).
    """

    service_type = "agents"
    singleton = False

    system_prompt = "You are an Agent in the Cheshire Cat AI fleet. Help the user and other agents with their requests."
    model = None  # a slug like "openai:gpt-4o"; if None, taken from core settings

    # Directives attached to this agent. Each entry may be a Directive instance,
    # a Directive subclass, or a registered directive slug (str). They are
    # resolved to live instances per run by `_resolve_directives()`.
    directives: List["Directive | type[Directive] | str"] = []

    # Safety cap on the agentic loop's tool-call ping-pong within a single run.
    # `None` means unbounded — the right default for long-running agents, which
    # bound themselves (re-invoked per message, or awaiting external events).
    # Set an int to stop and log after that many turns (runaway protection).
    max_iterations: int | None = None

    args: BaseModel | None = None

    async def __call__(self, task: Task) -> TaskResult:
        """
        Main entry point: run the agent like a function. Sets up run state,
        fires lifecycle hooks, and runs the agentic loop.
        """

        self._validate_args(task)

        # Per-run state on a fresh instance.
        self.task = task
        self.result = TaskResult()
        self.system_prompt = await self.get_system_prompt()
        self.tools = await self.list_tools()
        # AG-UI client tools share the provider's tool schema but retain their
        # client execution marker so they cannot enter Python or MCP execution.
        self.tools.extend(task._client_tools)
        self.directives = await self._resolve_directives()

        # data-only hook: mutate the Task in place or return a replacement.
        # Per-agent scoping is a directive's job, not a {slug} hook variant.
        self.task = await execute_hook("before_agent_run", self.task)

        self._validate_client_tool_namespace()
        await self.start()
        # Directives may add MCP or plugin tools during start, so validate again
        # before any provider can observe an ambiguous client/server name.
        self._validate_client_tool_namespace()
        await self.loop()
        await self.finish()

        # data-only hook: mutate the TaskResult in place or return a replacement.
        self.result = await execute_hook("after_agent_run", self.result)

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

        iteration = 0
        while True:

            # Runaway protection: stop if a finite cap is set and reached.
            iteration += 1
            if self.max_iterations is not None and iteration > self.max_iterations:
                log.warning(
                    f"Agent '{self.slug}' hit max_iterations={self.max_iterations}; "
                    "stopping the loop. Raise max_iterations or set it to None to allow more turns."
                )
                return

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
                # Server tools execute immediately. Client tools only emit their
                # AG-UI call events; the frontend returns results in a later run.
                waiting_for_client = False
                for tool_call in llm_mex.tool_calls:
                    selected_tool = self._find_tool(tool_call.name)
                    if selected_tool is not None and selected_tool.is_client_side:
                        waiting_for_client = True
                        continue
                    tool_message = await self.call_tool(tool_call)
                    self.result.messages.append(tool_message)

                if waiting_for_client:
                    return

    async def get_system_prompt(self) -> str:
        """
        Build the system prompt from the agent's own configuration.

        For a static prompt just set the class attribute `Agent.system_prompt`.
        Override this method for dynamic behavior. To shape the prompt
        cross-cuttingly, append to `agent.system_prompt` from a directive's
        `start()` (persistent) or `step()` (per-turn) — prompt shaping is a
        directive's job, not a hook's.
        """

        return type(self).system_prompt

    async def list_tools(self) -> List[Tool]:
        """
        The tools this agent can call: its own `@tool` methods (including any
        inherited from base classes or mixins).

        Tools are agent-scoped — an agent does NOT silently inherit every plugin's
        tools. To share tools across agents, put them on a mixin and inherit it;
        to add or filter tools cross-cuttingly, mutate `agent.tools` from a
        directive's `start()` — tool shaping is a directive's job, not a hook's.
        MCP tools are contributed this way, by the MCP plugin's directive.
        """

        # Agent's own internal tools (own + inherited via the class MRO)
        return self.instantiate_agent_tools()

    async def _resolve_directives(self) -> List["Directive"]:
        """
        Normalise the declared `directives` list into live instances.

        Each entry may be:
        - a Directive instance      -> used as declared (author already configured it)
        - a Directive subclass      -> resolved through the registry by its slug
        - a registered slug (str)   -> resolved through the registry

        The registry forms inject typed settings and run `setup()`, just like any
        other service.
        """
        from cat.ambient.runtime import ccat
        from cat.base import Directive

        resolved: List["Directive"] = []
        for d in self.directives:
            if isinstance(d, Directive):
                resolved.append(d)
            elif isclass(d) and issubclass(d, Directive):
                resolved.append(await ccat().get("directives", d.slug, raise_error=True))
            elif isinstance(d, str):
                resolved.append(await ccat().get("directives", d, raise_error=True))
            else:
                raise TypeError(
                    f"Invalid directive {d!r} on agent '{self.slug}': "
                    "expected a Directive instance, subclass, or registered slug."
                )
        return resolved

    async def call_tool(self, tool_call, *args, **kwargs):
        """Call a tool, or tell the model it named one that doesn't exist.

        Models hallucinate tool names. That is a normal turn in the loop, not a
        crash: we hand the error back as the tool result and let the model try
        again with a name from the list, exactly as it would recover from a tool
        that raised.
        """

        name = tool_call.name
        selected_tool = self._find_tool(name)
        if selected_tool is not None:
            if selected_tool.is_client_side:
                # Keep direct or future call sites from bypassing the loop's
                # client-side execution boundary.
                raise RuntimeError(
                    f"Client tool '{name}' must be executed by the AG-UI client."
                )
            return await selected_tool.execute(self, tool_call)

        available = ", ".join(sorted(t.name for t in self.tools)) or "none"
        log.warning(
            f"Agent '{self.slug}': LLM called unknown tool '{name}'. Available: {available}."
        )
        return Message(
            role="tool",
            tool_call_id=str(tool_call.id),
            content=[TextContent(
                text=f"Tool '{name}' not found. Available tools: {available}."
            )],
        )

    def _find_tool(self, name: str) -> Tool | None:
        """Resolve an offered tool by its provider-visible name."""

        return next((tool for tool in self.tools if tool.name == name), None)

    def _validate_client_tool_namespace(self) -> None:
        """Reject ambiguity between client tools and server-owned implementations."""

        client_names = {
            tool.name for tool in self.tools if tool.is_client_side
        }
        conflicts = sorted(
            name
            for name in client_names
            if sum(tool.name == name for tool in self.tools) > 1
        )
        if conflicts:
            # Reject instead of choosing precedence: silent shadowing could run a
            # server tool when the frontend expected to retain execution control.
            raise ValueError(
                "Client tool names conflict with other available tools: "
                + ", ".join(conflicts)
                + "."
            )

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
