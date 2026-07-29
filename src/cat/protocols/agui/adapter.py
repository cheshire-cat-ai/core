import json
import re
from typing import Any

from ag_ui.core import (
    ActivityMessage,
    AssistantMessage,
    BinaryInputContent,
    Context,
    DeveloperMessage,
    InputContent,
    Message as AGUIMessage,
    ReasoningMessage,
    RunAgentInput,
    SystemMessage,
    TextInputContent,
    Tool as AGUITool,
    ToolCall as AGUIToolCall,
    ToolMessage,
    UserMessage,
)

from cat.mad_hatter.decorators import Tool
from cat.protocols.model_context.type_wrappers import Resource
from cat.types import ImageContent, Message, Task, TextContent, ToolCall


# Client schemas are untrusted request data and are resent to the model on every
# turn. Conservative limits bound token and serialization cost per request.
MAX_CLIENT_TOOLS = 32
MAX_TOOL_DESCRIPTION_LENGTH = 4_096
MAX_TOOL_SCHEMA_BYTES = 65_536
MAX_TOOL_SCHEMA_DEPTH = 32
TOOL_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


class AGUIInputError(ValueError):
    """Raised when valid AG-UI data cannot be represented safely by a Cat Task."""


def run_agent_input_to_task(input_data: RunAgentInput) -> Task:
    """Convert supported AG-UI input fields to Cheshire Cat's internal Task."""

    args = _convert_forwarded_props(input_data.forwarded_props)
    client_tools = _convert_client_tools(input_data.tools)
    messages = [
        converted
        for message in input_data.messages
        if (converted := _convert_message(message)) is not None
    ]
    resources = [
        _convert_context(context, index)
        for index, context in enumerate(input_data.context)
    ]

    # AG-UI state is not copied until Cat can emit synchronized state updates.
    # One-way ingestion would make clients believe state support is complete.
    task = Task(
        messages=messages,
        resources=resources,
        args=args,
        stream=True,
    )
    # The private field keeps client execution semantics out of the public Task
    # schema while carrying validated definitions through the normal agent path.
    task._client_tools = client_tools
    return task


def _convert_client_tools(tools: list[AGUITool]) -> list[Tool]:
    if len(tools) > MAX_CLIENT_TOOLS:
        raise AGUIInputError(
            f"AG-UI requests may provide at most {MAX_CLIENT_TOOLS} client tools."
        )

    converted = []
    names = set()
    for tool in tools:
        if not TOOL_NAME_PATTERN.fullmatch(tool.name):
            raise AGUIInputError(
                "AG-UI tool names must contain 1-64 letters, digits, "
                "underscores, or hyphens."
            )
        if tool.name in names:
            raise AGUIInputError(f"Duplicate AG-UI tool name: '{tool.name}'.")
        if len(tool.description) > MAX_TOOL_DESCRIPTION_LENGTH:
            raise AGUIInputError(
                f"AG-UI tool '{tool.name}' description is too long."
            )

        # Descriptions and schema annotations remain verbatim because they are
        # the frontend's model-facing contract. Safety comes from deferring
        # execution to that frontend, not from rewriting its tool semantics.
        schema = _validate_tool_schema(tool)
        names.add(tool.name)
        converted.append(
            Tool.from_client_definition(
                name=tool.name,
                description=tool.description,
                input_schema=schema,
            )
        )

    return converted


def _validate_tool_schema(tool: AGUITool) -> dict[str, Any]:
    if not isinstance(tool.parameters, dict):
        raise AGUIInputError(
            f"AG-UI tool '{tool.name}' parameters must be a JSON Schema object."
        )

    schema = dict(tool.parameters)
    if schema.get("type") != "object":
        # Cheshire Cat tool calls always carry a JSON object in ToolCall.args.
        # Requiring the same shape avoids provider-specific coercion.
        raise AGUIInputError(
            f"AG-UI tool '{tool.name}' parameters must have type 'object'."
        )

    if _json_depth(schema) > MAX_TOOL_SCHEMA_DEPTH:
        raise AGUIInputError(f"AG-UI tool '{tool.name}' schema is too deeply nested.")

    try:
        encoded = json.dumps(
            schema,
            allow_nan=False,
            separators=(",", ":"),
        ).encode("utf-8")
    except (OverflowError, RecursionError, TypeError, ValueError) as error:
        raise AGUIInputError(
            f"AG-UI tool '{tool.name}' parameters must contain valid JSON values."
        ) from error

    if len(encoded) > MAX_TOOL_SCHEMA_BYTES:
        raise AGUIInputError(f"AG-UI tool '{tool.name}' schema is too large.")

    return schema


def _json_depth(value: Any) -> int:
    """Measure JSON nesting iteratively so hostile schemas cannot recurse Python."""

    maximum = 1
    pending = [(value, 1)]
    seen_containers = set()
    while pending:
        current, depth = pending.pop()
        maximum = max(maximum, depth)
        if isinstance(current, dict):
            if id(current) in seen_containers:
                continue
            seen_containers.add(id(current))
            pending.extend((child, depth + 1) for child in current.values())
        elif isinstance(current, list):
            if id(current) in seen_containers:
                continue
            seen_containers.add(id(current))
            pending.extend((child, depth + 1) for child in current)
    return maximum


def _convert_forwarded_props(forwarded_props: Any) -> dict[str, Any]:
    if forwarded_props is None:
        return {}
    if not isinstance(forwarded_props, dict):
        raise AGUIInputError(
            "AG-UI forwardedProps must be an object to map to Task.args."
        )
    return dict(forwarded_props)


def _convert_context(context: Context, index: int) -> Resource:
    # AG-UI Context has no URI. A deterministic protocol URI preserves ordering
    # while the extra value field keeps the original text available to directives.
    return Resource(
        name=context.description,
        uri=f"agui://context/{index}",
        description=context.description,
        mimeType="text/plain",
        value=context.value,
    )


def _convert_message(message: AGUIMessage) -> Message | None:
    if isinstance(message, UserMessage):
        return Message(
            role="user",
            content=_convert_user_content(message.content),
        )

    if isinstance(message, AssistantMessage):
        content = [TextContent(text=message.content)] if message.content else []
        tool_calls = [
            _convert_tool_call(tool_call) for tool_call in message.tool_calls or []
        ]
        return Message(
            role="assistant",
            content=content,
            tool_calls=tool_calls,
        )

    if isinstance(message, ToolMessage):
        content = message.content
        if message.error:
            # Cat has no separate tool-error field, so keep the failure visible
            # to the model in the tool result that it already understands.
            content = f"{content}\nTool error: {message.error}".strip()
        return Message(
            role="tool",
            content=[TextContent(text=content)],
            tool_call_id=message.tool_call_id,
        )

    if isinstance(message, (DeveloperMessage, SystemMessage)):
        # The backend agent owns its system prompt. Client history must not
        # silently override that security and behavior boundary.
        return None

    if isinstance(message, (ActivityMessage, ReasoningMessage)):
        # These roles describe UI progress or hidden reasoning, not LLM turns
        # supported by Cat's provider-neutral Message model.
        return None

    raise AGUIInputError(f"Unsupported AG-UI message type: {type(message).__name__}.")


def _convert_user_content(
    content: str | list[InputContent],
) -> list[TextContent | ImageContent]:
    if isinstance(content, str):
        return [TextContent(text=content)]

    blocks = []
    for block in content:
        if isinstance(block, TextInputContent):
            blocks.append(TextContent(text=block.text))
        elif isinstance(block, BinaryInputContent):
            blocks.append(_convert_binary_content(block))
        else:
            raise AGUIInputError(
                f"Unsupported AG-UI content type: {type(block).__name__}."
            )
    return blocks


def _convert_binary_content(content: BinaryInputContent) -> ImageContent:
    if not content.mime_type.startswith("image/"):
        raise AGUIInputError(
            f"AG-UI binary MIME type '{content.mime_type}' is not supported."
        )
    if content.data is None:
        # Cat providers currently consume inline base64 images. Fetching URLs or
        # resolving client attachment IDs inside the adapter would be ambiguous.
        raise AGUIInputError("AG-UI images must provide inline base64 data.")

    data = content.data
    if data.startswith("data:"):
        header, separator, payload = data.partition(",")
        expected_header = f"data:{content.mime_type};base64"
        if not separator or header != expected_header:
            raise AGUIInputError("AG-UI image data URL does not match its mimeType.")
        data = payload

    metadata = {"filename": content.filename} if content.filename else None
    return ImageContent(
        data=data,
        mimeType=content.mime_type,
        _meta=metadata,
    )


def _convert_tool_call(tool_call: AGUIToolCall) -> ToolCall:
    arguments = tool_call.function.arguments or "{}"
    try:
        args = json.loads(arguments)
    except json.JSONDecodeError as error:
        raise AGUIInputError(
            f"AG-UI tool call '{tool_call.id}' has invalid JSON arguments."
        ) from error

    if not isinstance(args, dict):
        raise AGUIInputError(
            f"AG-UI tool call '{tool_call.id}' arguments must be a JSON object."
        )

    return ToolCall(
        id=tool_call.id,
        name=tool_call.function.name,
        args=args,
    )
