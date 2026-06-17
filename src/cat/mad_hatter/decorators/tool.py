import inspect
import time
from uuid import uuid4
from typing import Callable, List, Dict, TYPE_CHECKING

from fastmcp.tools.tool import FunctionTool, ParsedFunction
from fastmcp.client.client import CallToolResult

from cat.protocols.agui import events
from cat.utils import run_sync_or_async

if TYPE_CHECKING:
    from cat.types import Message
    from cat.types.messages import TextContent

class Tool:
    """Cat tool uniforming @tool decorated functions in plugins and MCP tools."""

    def __init__(
        self,
        func: Callable,
        name: str,
        description: str,
        input_schema: Dict,
        output_schema: Dict,
        is_internal: bool = True,
        return_direct: bool = False,
        examples: List[str] = [],
    ):
        self.func = func
        self.name = name 
        self.description = description 
        self.input_schema = input_schema 
        self.output_schema = output_schema

        self.return_direct = return_direct
        self.examples = examples
        self.is_internal = is_internal
    
        # will be assigned by MadHatter
        self.plugin_id = None

    @classmethod
    def from_decorated_function(
        cls,
        func: Callable,
        return_direct: bool = False,
        examples: List[str] = []
    ) -> 'Tool':
        
        parsed_function = ParsedFunction.from_function(
            func,
            exclude_args=["caller", "self"], # awesome, will only be used at execution
            validate=False
        )

        return cls(
            func,
            name = parsed_function.name,
            description = parsed_function.description,
            input_schema = parsed_function.input_schema,
            output_schema = parsed_function.output_schema,
            return_direct = return_direct,
            examples = examples
        )

    @classmethod
    def from_fastmcp(
        cls,
        t: FunctionTool,
        mcp_client_func: Callable
    ) -> "Tool":
        
        return cls(
            func = mcp_client_func,
            name = t.name,
            description = t.description or t.name,
            input_schema = t.inputSchema,
            output_schema = t.outputSchema,
            is_internal = False
        )
    
    def __repr__(self) -> str:
        return f"Tool(name={self.name}, input_schema={self.input_schema}, internal={self.is_internal})"

    async def execute(self, agent, tool_call) -> "Message":
        """
        Execute a Tool with the provided tool_call data structure (which is returned by the LLM).
        Will emit a ToolCallResult AGUI event and return a Message with role="tool".

        Parameters
        ----------
        agent : Agent
            Agent calling the tool.
        tool_call : dict
            Dictionary representing the choice of tool and its args (produced by LLM)

        Returns
        -------
        Message
            A Message with role="tool" and the tool output.
        """

        # execute the tool
        try:
            if self.is_internal:
                # internal tool — ambient state (user, capabilities) comes from
                # `from cat import ...`, not a passed `caller`.
                tool_result: str = await run_sync_or_async(
                    self.func, **tool_call.args
                )
            else:
                # MCP tool
                async with agent.mcp:
                    tool_result: CallToolResult = await self.func(self.name, tool_call.args)
        except Exception as e:
            tool_result = f"Error: {e}"

        # Standardize output
        tool_result = self.standardize_output(tool_call, tool_result)

        # Emit AGUI result event
        await self.emit_agui_tool_result_event(agent, tool_call, tool_result)

        # TODOV2: should return CallToolResult directly
        #   Only supporting text for now
        #   https://modelcontextprotocol.info/specification/2024-11-05/server/tools/#tool-result
        return tool_result

    def standardize_output(self, tool_call, tool_result):

        from cat.types import Message, TextContent

        if isinstance(tool_result, str):
            # legacy tools returning plain string
            content_blocks = [TextContent(text=tool_result)]
        elif isinstance(tool_result, Message):
            # returning the output of .llm() directly
            content_blocks = tool_result.content
        elif isinstance(tool_result, CallToolResult):
            # MCP tool result - extract content blocks
            content_blocks = list(tool_result.content)
        else:
            # fallback: convert to string
            content_blocks = [TextContent(text=str(tool_result))]

        return Message(
            role="tool",
            content=content_blocks,
            tool_call_id=tool_call.id,
        )

    async def emit_agui_tool_result_event(self, agent, tool_call, tool_output):
        await agent.agui_event(
            events.ToolCallResultEvent(
                timestamp=int(time.time()),
                message_id=str(uuid4()),
                tool_call_id=str(tool_call.id),
                content=tool_output.text,
                raw_event=tool_output.model_dump()
            )
        )

    def bind_to(self, instance) -> 'Tool':
        """Bind this tool's function to an instance (for class-based tools)."""

        original_func = self.func
        sig = inspect.signature(original_func)
        valid_params = set(sig.parameters.keys()) - {'self'}

        # Bind the method
        bound_method = original_func.__get__(instance, instance.__class__)

        # Create wrapper
        def create_bound_wrapper(bound_func, params):
            async def wrapper(**kwargs):
                filtered_kwargs = {k: v for k, v in kwargs.items() if k in params}
                if inspect.iscoroutinefunction(bound_func):
                    return await bound_func(**filtered_kwargs)
                else:
                    return bound_func(**filtered_kwargs)

            return wrapper

        # Return a NEW Tool with the bound function
        return Tool(
            func=create_bound_wrapper(bound_method, valid_params),
            name=self.name,
            description=self.description,
            input_schema=self.input_schema,
            output_schema=self.output_schema,
            return_direct=self.return_direct,
            examples=self.examples,
            is_internal=self.is_internal
        )


def tool(*args, return_direct: bool = False, examples: List[str] = []) -> Tool:

    if len(args) == 1 and callable(args[0]):
        return Tool.from_decorated_function(
            args[0],
            return_direct=return_direct,
            examples=examples
        )
    else:
        def wrapper(func):
            return Tool.from_decorated_function(
                func,
                return_direct=return_direct,
                examples=examples
            )
        return wrapper


