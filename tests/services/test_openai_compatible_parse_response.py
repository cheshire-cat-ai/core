"""parse_response() must handle zero-argument tool calls.

Many OpenAI-compatible backends (Ollama, vLLM, LM Studio, ...) return
`arguments: ""` for a tool call that takes no arguments. The streaming path
(stream_completion) already guards this with `json.loads(tc["args_str"] or
"{}")`; the non-streaming path (parse_response) didn't, so the same
zero-argument tool call crashed the whole turn with JSONDecodeError instead
of parsing to an empty-args ToolCall.
"""

from types import SimpleNamespace

from cat.services.model_providers.openai_compatible import OpenAICompatibleProvider


def make_response(arguments):
    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    content=None,
                    tool_calls=[
                        SimpleNamespace(
                            id="call_1",
                            function=SimpleNamespace(
                                name="get_time", arguments=arguments
                            ),
                        )
                    ],
                )
            )
        ]
    )


def test_parse_response_empty_arguments_string():
    provider = object.__new__(OpenAICompatibleProvider)

    message = provider.parse_response(make_response(""))

    assert len(message.tool_calls) == 1
    assert message.tool_calls[0].name == "get_time"
    assert message.tool_calls[0].args == {}


def test_parse_response_normal_arguments_still_parsed():
    provider = object.__new__(OpenAICompatibleProvider)

    message = provider.parse_response(make_response('{"city": "Rome"}'))

    assert message.tool_calls[0].args == {"city": "Rome"}
