
from langchain.schema import AgentAction, AgentFinish

from cat.looking_glass.output_parser import ChooseProcedureOutputParser


def test_procedure_output_parser():
    
    parser = ChooseProcedureOutputParser()

    # badly formatted output
    out = parser.parse("not a JSON")
    assert isinstance(out, AgentFinish)
    assert out.return_values == {"output": None}

    # json with wrong keys
    out = parser.parse('{"wrong_key": "any_value"}')
    assert isinstance(out, AgentFinish)
    assert out.return_values == {"output": None}

    # final answer
    out = parser.parse('{"action": "final_answer"}')
    assert isinstance(out, AgentFinish)
    assert out.return_values == {"output": None}

    # action without action_input
    out = parser.parse('{"action": "some_action"}')
    assert isinstance(out, AgentAction)
    assert out.tool == "some_action"
    assert out.tool_input == ""

    # action with action_input None
    out = parser.parse('{"action": "some_action", "action_input": null}')
    assert isinstance(out, AgentAction)
    assert out.tool == "some_action"
    assert out.tool_input == ""

    # action with action_input string
    out = parser.parse('{"action": "some_action", "action_input": "some_input"}')
    assert isinstance(out, AgentAction)
    assert out.tool == "some_action"
    assert out.tool_input == "some_input"

    # action with action_input int
    out = parser.parse('{"action": "some_action", "action_input": 42}')
    assert isinstance(out, AgentAction)
    assert out.tool == "some_action"
    assert out.tool_input == "42"

    # action with action_input float
    out = parser.parse('{"action": "some_action", "action_input": 3.14}')
    assert isinstance(out, AgentAction)
    assert out.tool == "some_action"
    assert out.tool_input == "3.14"

    # action with action_input bool
    out = parser.parse('{"action": "some_action", "action_input": true}')
    assert isinstance(out, AgentAction)
    assert out.tool == "some_action"
    assert out.tool_input == "true"

    # action with action_input dict
    out = parser.parse('{"action": "some_action", "action_input": {"key": "value"}}')
    assert isinstance(out, AgentAction)
    assert out.tool == "some_action"
    assert out.tool_input == '{"key": "value"}'

    # action with action_input list
    out = parser.parse('{"action": "some_action", "action_input": ["a", 2, true]}')
    assert isinstance(out, AgentAction)
    assert out.tool == "some_action"
    assert out.tool_input == '["a", 2, true]'