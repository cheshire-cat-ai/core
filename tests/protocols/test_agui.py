import pytest
from ag_ui.core import RunAgentInput

from cat.protocols.agui.adapter import (
    AGUIInputError,
    MAX_CLIENT_TOOLS,
    MAX_TOOL_DESCRIPTION_LENGTH,
    MAX_TOOL_SCHEMA_BYTES,
    MAX_TOOL_SCHEMA_DEPTH,
    run_agent_input_to_task,
)
from cat.services.model_providers.openai_compatible import OpenAICompatibleProvider
from cat.types import ImageContent, Task


def _run_input(**overrides) -> RunAgentInput:
    payload = {
        "threadId": "thread-1",
        "runId": "run-1",
        "state": {},
        "messages": [],
        "tools": [],
        "context": [],
        "forwardedProps": {},
    }
    payload.update(overrides)
    return RunAgentInput.model_validate(payload)


def test_run_agent_input_maps_supported_task_fields():
    input_data = _run_input(
        state={"clientOnly": True},
        messages=[
            {"id": "system-1", "role": "system", "content": "client system"},
            {"id": "user-1", "role": "user", "content": "hello"},
            {
                "id": "assistant-1",
                "role": "assistant",
                "content": "calling",
                "toolCalls": [
                    {
                        "id": "call-1",
                        "function": {
                            "name": "lookup",
                            "arguments": '{"query": "cat"}',
                        },
                    }
                ],
            },
            {
                "id": "tool-1",
                "role": "tool",
                "content": "failed",
                "toolCallId": "call-1",
                "error": "not found",
            },
            {
                "id": "activity-1",
                "role": "activity",
                "activityType": "SEARCH",
                "content": {"status": "done"},
            },
            {
                "id": "reasoning-1",
                "role": "reasoning",
                "content": "private reasoning",
            },
        ],
        context=[{"description": "Customer", "value": "Alice"}],
        forwardedProps={"temperature": 0.2},
    )

    task = run_agent_input_to_task(input_data)

    assert task.stream is True
    assert task.args == {"temperature": 0.2}
    assert [message.role for message in task.messages] == [
        "user",
        "assistant",
        "tool",
    ]
    assert task.messages[0].text == "hello"
    assert task.messages[1].tool_calls[0].name == "lookup"
    assert task.messages[1].tool_calls[0].args == {"query": "cat"}
    assert task.messages[2].tool_call_id == "call-1"
    assert task.messages[2].text == "failed\nTool error: not found"
    assert str(task.resources[0].uri) == "agui://context/0"
    assert task.resources[0].name == "Customer"
    assert task.resources[0].model_extra["value"] == "Alice"
    assert "clientOnly" not in task.args


def test_run_agent_input_maps_text_and_inline_image_content():
    input_data = _run_input(
        messages=[
            {
                "id": "user-1",
                "role": "user",
                "content": [
                    {"type": "text", "text": "describe"},
                    {
                        "type": "binary",
                        "mimeType": "image/png",
                        "data": "data:image/png;base64,aW1hZ2U=",
                        "filename": "cat.png",
                    },
                ],
            }
        ]
    )

    task = run_agent_input_to_task(input_data)

    assert task.messages[0].text == "describe"
    image = task.messages[0].content[1]
    assert isinstance(image, ImageContent)
    assert image.data == "aW1hZ2U="
    assert image.mimeType == "image/png"
    assert image.meta == {"filename": "cat.png"}


def test_run_agent_input_maps_client_provided_tools_as_runtime_only():
    input_data = _run_input(
        tools=[
            {
                "name": "confirm_action",
                "description": "Ask the user to confirm an action.",
                "parameters": {
                    "type": "object",
                    "properties": {"message": {"type": "string"}},
                    "required": ["message"],
                },
            }
        ]
    )

    task = run_agent_input_to_task(input_data)
    client_tool = task._client_tools[0]

    assert client_tool.name == "confirm_action"
    assert client_tool.input_schema["required"] == ["message"]
    assert client_tool.is_client_side
    assert "_client_tools" not in task.model_dump()

    provider_tool = OpenAICompatibleProvider().build_tools([client_tool])[0]
    assert provider_tool["function"]["name"] == "confirm_action"
    assert provider_tool["function"]["parameters"]["required"] == ["message"]


async def test_client_tool_has_no_server_execution_path():
    task = run_agent_input_to_task(
        _run_input(
            tools=[
                {
                    "name": "confirm_action",
                    "description": "Ask for confirmation.",
                    "parameters": {"type": "object"},
                }
            ]
        )
    )

    with pytest.raises(RuntimeError, match="must be executed by the AG-UI client"):
        await task._client_tools[0].execute(None, None)


def test_task_json_cannot_inject_runtime_client_tools():
    task = Task.model_validate(
        {
            "messages": [],
            "stream": False,
            "_client_tools": [
                {
                    "name": "server_command",
                    "description": "Should never be accepted.",
                    "parameters": {"type": "object"},
                }
            ],
        }
    )

    assert task._client_tools == []


@pytest.mark.parametrize(
    ("tools", "error"),
    [
        (
            [
                {
                    "name": "duplicate",
                    "description": "First.",
                    "parameters": {"type": "object"},
                },
                {
                    "name": "duplicate",
                    "description": "Second.",
                    "parameters": {"type": "object"},
                },
            ],
            "Duplicate AG-UI tool name",
        ),
        (
            [
                {
                    "name": "contains spaces",
                    "description": "Invalid provider name.",
                    "parameters": {"type": "object"},
                }
            ],
            "tool names must contain",
        ),
        (
            [
                {
                    "name": "wrong_schema",
                    "description": "Invalid argument shape.",
                    "parameters": {"type": "array"},
                }
            ],
            "must have type 'object'",
        ),
        (
            [
                {
                    "name": "not_a_schema",
                    "description": "Invalid argument schema.",
                    "parameters": [],
                }
            ],
            "JSON Schema object",
        ),
    ],
)
def test_run_agent_input_rejects_unsafe_client_tool_definitions(tools, error):
    with pytest.raises(AGUIInputError, match=error):
        run_agent_input_to_task(_run_input(tools=tools))


def test_run_agent_input_limits_client_tool_count():
    tools = [
        {
            "name": f"client_tool_{index}",
            "description": "Frontend tool.",
            "parameters": {"type": "object"},
        }
        for index in range(MAX_CLIENT_TOOLS + 1)
    ]

    with pytest.raises(AGUIInputError, match="at most"):
        run_agent_input_to_task(_run_input(tools=tools))


def test_run_agent_input_limits_client_tool_schema_depth():
    schema = {"type": "object"}
    cursor = schema
    for _ in range(MAX_TOOL_SCHEMA_DEPTH):
        child = {"type": "object"}
        cursor["properties"] = {"child": child}
        cursor = child

    with pytest.raises(AGUIInputError, match="too deeply nested"):
        run_agent_input_to_task(
            _run_input(
                tools=[
                    {
                        "name": "deep_schema",
                        "description": "Frontend tool.",
                        "parameters": schema,
                    }
                ]
            )
        )


@pytest.mark.parametrize(
    ("description", "parameters", "error"),
    [
        (
            "x" * (MAX_TOOL_DESCRIPTION_LENGTH + 1),
            {"type": "object"},
            "description is too long",
        ),
        (
            "Frontend tool.",
            {
                "type": "object",
                "description": "x" * MAX_TOOL_SCHEMA_BYTES,
            },
            "schema is too large",
        ),
    ],
)
def test_run_agent_input_limits_client_tool_payload_size(
    description,
    parameters,
    error,
):
    with pytest.raises(AGUIInputError, match=error):
        run_agent_input_to_task(
            _run_input(
                tools=[
                    {
                        "name": "bounded_tool",
                        "description": description,
                        "parameters": parameters,
                    }
                ]
            )
        )


def test_run_agent_input_rejects_non_object_forwarded_props():
    input_data = _run_input(forwardedProps="invalid")

    with pytest.raises(AGUIInputError, match="forwardedProps must be an object"):
        run_agent_input_to_task(input_data)


def test_run_agent_input_rejects_invalid_tool_call_arguments():
    input_data = _run_input(
        messages=[
            {
                "id": "assistant-1",
                "role": "assistant",
                "toolCalls": [
                    {
                        "id": "call-1",
                        "function": {
                            "name": "lookup",
                            "arguments": "not-json",
                        },
                    }
                ],
            }
        ]
    )

    with pytest.raises(AGUIInputError, match="invalid JSON arguments"):
        run_agent_input_to_task(input_data)


@pytest.mark.parametrize(
    "binary",
    [
        {"type": "binary", "mimeType": "audio/wav", "data": "YXVkaW8="},
        {
            "type": "binary",
            "mimeType": "image/png",
            "url": "https://example.com/cat.png",
        },
    ],
)
def test_run_agent_input_rejects_unsupported_binary_content(binary):
    input_data = _run_input(
        messages=[
            {
                "id": "user-1",
                "role": "user",
                "content": [binary],
            }
        ]
    )

    with pytest.raises(AGUIInputError):
        run_agent_input_to_task(input_data)
