import inspect
import time
from uuid import uuid4
from dataclasses import dataclass, field
from functools import wraps
from typing import Callable, Dict, List, Optional, TYPE_CHECKING

from fastmcp.tools.function_tool import FunctionTool, ParsedFunction
from fastmcp.client.client import CallToolResult

from cat.ambient import agui_event
from cat.ambient.runtime import use_plugin
from cat.protocols.agui import events
from cat.utils import run_sync_or_async

if TYPE_CHECKING:
    from cat.types import Message


@dataclass
class ToolMeta:
    """UI metadata derived from an MCP tool's `_meta.ui` (MCP Apps).

    - `resource_uri`: a `ui://` URI declaring the tool's UI. `None` = a plain,
      non-UI tool.
    - `visibility`: who may invoke the tool. `["model"]` (the default) means it is
      offered to the LLM; `["app"]` means app-only — hidden from the LLM and
      reserved for the future UI bridge. Both (`["model", "app"]`) is model-visible.
    """

    resource_uri: Optional[str] = None
    visibility: List[str] = field(default_factory=lambda: ["model"])

    @property
    def is_model_visible(self) -> bool:
        """Whether this tool should be offered to the LLM."""
        return "model" in self.visibility


def _without_params(func: Callable, excluded: set) -> Callable:
    """A view of `func` with `excluded` parameters dropped, for schema use only."""
    sig = inspect.signature(func)
    kept_params = [p for name, p in sig.parameters.items() if name not in excluded]

    if len(kept_params) == len(sig.parameters):
        return func

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    wrapper.__signature__ = inspect.Signature(
        kept_params, return_annotation=sig.return_annotation
    )
    return wrapper


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
        meta: Optional[ToolMeta] = None,
    ):
        self.func = func
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.output_schema = output_schema

        self.is_internal = is_internal

        # UI metadata (resource_uri, visibility). Absent = non-UI, model-visible.
        self.meta = meta or ToolMeta()

        # will be assigned by MadHatter
        self.plugin_id = None

    @classmethod
    def from_decorated_function(
        cls,
        func: Callable,
    ) -> 'Tool':

        # fastmcp 4.x dropped `exclude_args`; hide `self`/`caller` from the
        # schema ourselves, they're only bound/resolved at execution time.
        schema_func = _without_params(func, {"self", "caller"})

        parsed_function = ParsedFunction.from_function(
            schema_func,
            validate=False
        )

        return cls(
            func,
            name = parsed_function.name,
            description = parsed_function.description,
            input_schema = parsed_function.input_schema,
            output_schema = parsed_function.output_schema,
        )

    @classmethod
    def from_fastmcp(
        cls,
        t: FunctionTool,
        mcp_client_func: Callable
    ) -> "Tool":

        # MCP Apps UI metadata rides on the tool's `_meta.ui`:
        #   {"ui": {"resourceUri": "ui://...", "visibility": ["model", "app"]}}
        ui = (getattr(t, "meta", None) or {}).get("ui", {})
        meta = ToolMeta(
            resource_uri = ui.get("resourceUri"),
            visibility = ui.get("visibility") or ["model"],
        )

        return cls(
            func = mcp_client_func,
            name = t.name,
            description = t.description or t.name,
            input_schema = t.input_schema,
            output_schema = t.output_schema,
            is_internal = False,
            meta = meta,
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

        # a tool belongs to the plugin that defined the agent carrying it, so
        # `from cat import plugin` resolves while the tool body runs
        plugin_id = self.plugin_id or getattr(type(agent), "plugin_id", None)

        # execute the tool
        try:
            with use_plugin(plugin_id):
                if self.is_internal:
                    # internal tool — ambient state (user, capabilities) comes from
                    # `from cat import ...`, not a passed `caller`.
                    tool_result: str = await run_sync_or_async(
                        self.func, **tool_call.args
                    )
                else:
                    # MCP tool — the bound client function connects statelessly per call
                    tool_result: CallToolResult = await self.func(self.name, tool_call.args)
        except Exception as e:
            tool_result = f"Error: {e}"

        # Standardize output
        tool_result = self.standardize_output(tool_call, tool_result)

        # Emit AGUI result event
        await self.emit_agui_tool_result_event(tool_call, tool_result)

        # TODOV2: should return CallToolResult directly
        #   Only supporting text for now
        #   https://modelcontextprotocol.info/specification/2024-11-05/server/tools/#tool-result
        return tool_result

    def standardize_output(self, tool_call, tool_result):

        from cat.types import Message, TextContent

        # `structuredContent` is the machine-readable twin of a tool result, used
        # by MCP Apps to feed the widget. It is preserved on the Message but never
        # forwarded to LLM providers (see openai_compatible.convert_message).
        structured_content = None

        if isinstance(tool_result, str):
            # legacy tools returning plain string
            content_blocks = [TextContent(text=tool_result)]
        elif isinstance(tool_result, Message):
            # returning the output of .llm() directly
            content_blocks = tool_result.content
        elif isinstance(tool_result, CallToolResult):
            # MCP tool result — coerce each raw `mcp.types` block into the Cat
            # content-block wrappers (via its dict form). A `ui://` ResourceLink /
            # EmbeddedResource is preserved as a resource block, not degraded to text.
            content_blocks = [b.model_dump() for b in tool_result.content]
            structured_content = tool_result.structured_content
        else:
            # fallback: convert to string
            content_blocks = [TextContent(text=str(tool_result))]

        return Message(
            role="tool",
            content=content_blocks,
            tool_call_id=tool_call.id,
            structuredContent=structured_content,
        )

    async def emit_agui_tool_result_event(self, tool_call, tool_output):
        await agui_event(
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
            is_internal=self.is_internal,
            meta=self.meta,
        )


def tool(*args) -> Tool:

    if len(args) == 1 and callable(args[0]):
        return Tool.from_decorated_function(args[0])
    else:
        def wrapper(func):
            return Tool.from_decorated_function(func)
        return wrapper


