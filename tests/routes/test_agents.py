import asyncio
import json

from cat import tool
from cat.ambient.runtime import ccat
from cat.base import Agent


class ServerToolAgent(Agent):
    """Agent used to verify that client tools cannot shadow server code."""

    slug = "server-tool-agent"

    @tool
    def confirm_action(self, message: str):
        """Confirm an action on the server."""
        return message


def _agui_payload(**overrides) -> dict:
    payload = {
        "threadId": "thread-123",
        "runId": "run-456",
        "parentRunId": "run-parent",
        "state": {},
        "messages": [
            {
                "id": "message-789",
                "role": "user",
                "content": "Hello from AG-UI",
            }
        ],
        "tools": [],
        "context": [],
        "forwardedProps": {},
    }
    payload.update(overrides)
    return payload


def _sse_events(response) -> list[dict]:
    return [
        json.loads(line.removeprefix("data: "))
        for line in response.text.splitlines()
        if line.startswith("data: ")
    ]


async def test_agui_input_returns_compliant_sse(async_client, fake_llm):
    fake_llm.reply_text("Hello from Cat")

    response = await async_client.post(
        "/agents/default/message",
        json=_agui_payload(),
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")

    events = _sse_events(response)
    assert events[0]["type"] == "RUN_STARTED"
    assert events[0]["threadId"] == "thread-123"
    assert events[0]["runId"] == "run-456"
    assert events[0]["parentRunId"] == "run-parent"
    assert "thread_id" not in events[0]
    assert events[0]["timestamp"] > 1_000_000_000_000

    text_events = [
        event for event in events if event["type"].startswith("TEXT_MESSAGE")
    ]
    assert [event["type"] for event in text_events] == [
        "TEXT_MESSAGE_START",
        "TEXT_MESSAGE_CONTENT",
        "TEXT_MESSAGE_CONTENT",
        "TEXT_MESSAGE_CONTENT",
        "TEXT_MESSAGE_END",
    ]
    assert len({event["messageId"] for event in text_events}) == 1

    assert events[-1]["type"] == "RUN_FINISHED"
    assert events[-1]["threadId"] == "thread-123"
    assert events[-1]["runId"] == "run-456"
    assert fake_llm.calls[0].messages[-1].text == "Hello from AG-UI"


async def test_task_input_remains_available_without_streaming(async_client):
    response = await async_client.post(
        "/agents/default/message",
        json={
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": "Hello"}],
                }
            ],
            "stream": False,
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert response.json()["messages"][-1]["role"] == "assistant"


async def test_task_input_cannot_enable_streaming(async_client):
    response = await async_client.post(
        "/agents/default/message",
        json={
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": "Hello"}],
                }
            ],
            "stream": True,
        },
    )

    assert response.status_code == 422
    assert "RunAgentInput" in response.json()["detail"]


async def test_agui_client_tool_round_trip_runs_only_in_frontend(
    async_client,
    fake_llm,
):
    tool_definition = {
        "name": "confirm_action",
        "description": "Open a confirmation dialog in the frontend.",
        "parameters": {
            "type": "object",
            "properties": {"message": {"type": "string"}},
            "required": ["message"],
        },
    }
    fake_llm.reply_with_tool("confirm_action", message="Deploy now?")
    fake_llm.reply_text("The user confirmed the deployment.")

    first_response = await async_client.post(
        "/agents/default/message",
        json=_agui_payload(tools=[tool_definition]),
    )

    assert first_response.status_code == 200
    first_events = _sse_events(first_response)
    tool_events = [
        event for event in first_events if event["type"].startswith("TOOL_CALL")
    ]
    assert [event["type"] for event in tool_events] == [
        "TOOL_CALL_START",
        "TOOL_CALL_ARGS",
        "TOOL_CALL_END",
    ]
    assert tool_events[0]["toolCallName"] == "confirm_action"
    assert json.loads(tool_events[1]["delta"]) == {"message": "Deploy now?"}
    assert all(event["type"] != "TOOL_CALL_RESULT" for event in first_events)
    assert first_events[-1]["type"] == "RUN_FINISHED"
    assert len(fake_llm.calls) == 1
    assert fake_llm.calls[0].tools[0].is_client_side

    tool_call_id = tool_events[0]["toolCallId"]
    second_response = await async_client.post(
        "/agents/default/message",
        json=_agui_payload(
            runId="run-457",
            tools=[tool_definition],
            messages=[
                {
                    "id": "message-789",
                    "role": "user",
                    "content": "Deploy the application.",
                },
                {
                    "id": "assistant-tool-call",
                    "role": "assistant",
                    "toolCalls": [
                        {
                            "id": tool_call_id,
                            "function": {
                                "name": "confirm_action",
                                "arguments": '{"message":"Deploy now?"}',
                            },
                        }
                    ],
                },
                {
                    "id": "client-tool-result",
                    "role": "tool",
                    "toolCallId": tool_call_id,
                    "content": "confirmed",
                },
            ],
        ),
    )

    assert second_response.status_code == 200
    assert _sse_events(second_response)[-1]["type"] == "RUN_FINISHED"
    assert len(fake_llm.calls) == 2
    assert fake_llm.calls[1].messages[-1].role == "tool"
    assert fake_llm.calls[1].messages[-1].text == "confirmed"


async def test_agui_client_tool_cannot_shadow_server_tool(
    async_client,
    fake_llm,
):
    ccat().registry.register(ServerToolAgent)
    response = await async_client.post(
        "/agents/server-tool-agent/message",
        json=_agui_payload(
            tools=[
                {
                    "name": "confirm_action",
                    "description": "Frontend confirmation.",
                    "parameters": {"type": "object"},
                }
            ]
        ),
    )

    events = _sse_events(response)
    assert response.status_code == 200
    assert events[-1]["type"] == "RUN_ERROR"
    assert "conflict" in events[-1]["message"]
    assert fake_llm.calls == []


async def test_agui_client_and_server_tools_can_coexist(
    async_client,
    fake_llm,
):
    ccat().registry.register(ServerToolAgent)
    fake_llm.reply_with_tool("browser_dialog", message="Continue?")

    response = await async_client.post(
        "/agents/server-tool-agent/message",
        json=_agui_payload(
            tools=[
                {
                    "name": "browser_dialog",
                    "description": "Open a dialog in the browser.",
                    "parameters": {
                        "type": "object",
                        "properties": {"message": {"type": "string"}},
                    },
                }
            ]
        ),
    )

    events = _sse_events(response)
    assert response.status_code == 200
    assert events[-1]["type"] == "RUN_FINISHED"
    assert set(fake_llm.calls[0].tool_names) == {
        "browser_dialog",
        "confirm_action",
    }
    assert all(event["type"] != "TOOL_CALL_RESULT" for event in events)


async def test_agui_client_tools_are_isolated_between_concurrent_runs(
    async_client,
    fake_llm,
):
    fake_llm.reply_text("first response")
    fake_llm.reply_text("second response")

    async def run(message, tool_name):
        return await async_client.post(
            "/agents/default/message",
            json=_agui_payload(
                runId=f"run-{tool_name}",
                messages=[
                    {
                        "id": f"message-{tool_name}",
                        "role": "user",
                        "content": message,
                    }
                ],
                tools=[
                    {
                        "name": tool_name,
                        "description": "Tool scoped to one browser request.",
                        "parameters": {"type": "object"},
                    }
                ],
            ),
        )

    responses = await asyncio.gather(
        run("request alpha", "alpha_tool"),
        run("request beta", "beta_tool"),
    )

    assert all(response.status_code == 200 for response in responses)
    observed = {
        call.messages[-1].text: call.tool_names
        for call in fake_llm.calls
    }
    assert observed == {
        "request alpha": ["alpha_tool"],
        "request beta": ["beta_tool"],
    }


def test_agent_message_openapi_documents_both_protocol_modes(app):
    operation = app.openapi()["paths"]["/agents/{slug}/message"]["post"]

    request_schema = operation["requestBody"]["content"]["application/json"]["schema"]
    request_models = {
        variant["$ref"].rsplit("/", 1)[-1]
        for variant in request_schema["anyOf"]
    }
    response_content = operation["responses"]["200"]["content"]

    assert request_models == {"RunAgentInput", "Task"}
    assert set(response_content) == {"application/json", "text/event-stream"}
    assert response_content["application/json"]["schema"]["$ref"].endswith(
        "/TaskResult"
    )
