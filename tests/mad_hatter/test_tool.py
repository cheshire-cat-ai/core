from cat.mad_hatter.decorators.tool import Tool


class MockToolClass:
    def do_thing(self, caller, x: int) -> str:
        """Do a thing.

        Parameters
        ----------
        x : int
            an int
        """
        return str(x)


def test_from_decorated_function_excludes_self_and_caller_from_schema():
    t = Tool.from_decorated_function(MockToolClass.do_thing)

    assert "x" in t.input_schema["properties"]
    assert "self" not in t.input_schema["properties"]
    assert "caller" not in t.input_schema["properties"]


def test_from_decorated_function_keeps_output_schema():
    # regression: stripping params must keep the return annotation too
    t = Tool.from_decorated_function(MockToolClass.do_thing)

    assert t.output_schema is not None
    assert t.output_schema["properties"]["result"]["type"] == "string"
