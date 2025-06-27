

from cat.looking_glass.output_parser import ChooseProcedureOutputParser, LLMAction


def test_procedure_output_parser():
    
    parser = ChooseProcedureOutputParser()

    # badly formatted output
    out = parser.parse("not a JSON")
    assert isinstance(out, LLMAction)
    assert out.action is None
    assert out.action_input is None

    # json with wrong keys
    out = parser.parse('{"wrong_key": "any_value"}')
    assert isinstance(out, LLMAction)
    assert out.action is None
    assert out.action_input is None

    # no action
    out = parser.parse('{"action": "no_action"}')
    assert isinstance(out, LLMAction)
    assert out.action == "no_action"
    assert out.action_input is None

    # action without action_input
    out = parser.parse('{"action": "some_action"}')
    assert isinstance(out, LLMAction)
    assert out.action == "some_action"
    assert out.action_input is None

    # action with action_input null -> None
    out = parser.parse('{"action": "some_action", "action_input": null}')
    assert isinstance(out, LLMAction)
    assert out.action == "some_action"
    assert out.action_input is None

    # action with action_input string
    out = parser.parse('{"action": "some_action", "action_input": "some_input"}')
    assert isinstance(out, LLMAction)
    assert out.action == "some_action"
    assert out.action_input == "some_input"

    # additional content around the JSON
    out = parser.parse('whateverrr ```json{"action": "some_action", "action_input": "hey"} bla bla ```')
    assert isinstance(out, LLMAction)
    assert out.action == "some_action"
    assert out.action_input == "hey"

    # action with action_input int
    out = parser.parse('{"action": "some_action", "action_input": 42}')
    assert isinstance(out, LLMAction)
    assert out.action == "some_action"
    assert out.action_input == "42"

    # action with action_input float
    out = parser.parse('{"action": "some_action", "action_input": 3.14}')
    assert isinstance(out, LLMAction)
    assert out.action == "some_action"
    assert out.action_input == "3.14"

    # action with action_input bool
    out = parser.parse('{"action": "some_action", "action_input": true}')
    assert isinstance(out, LLMAction)
    assert out.action == "some_action"
    assert out.action_input == "true"

    # action with action_input dict
    out = parser.parse('{"action": "some_action", "action_input": {"key": "value"}}')
    assert isinstance(out, LLMAction)
    assert out.action == "some_action"
    assert out.action_input == '{"key": "value"}'

    # action with action_input list
    out = parser.parse('{"action": "some_action", "action_input": ["a", 2, true]}')
    assert isinstance(out, LLMAction)
    assert out.action == "some_action"
    assert out.action_input == '["a", 2, true]'

    # TODOV2: tools shoul receive in input  properly parsed types