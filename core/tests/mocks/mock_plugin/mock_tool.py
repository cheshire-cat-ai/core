from cat.mad_hatter.decorators import tool

tool_examples = ["mock tool example 1", "mock tool example 2"]

@tool(return_direct=True, examples=tool_examples)
def mock_tool(topic, cat):
    """Used to test mock tools. Input is the topic."""

    return f"A mock about {topic} :)"
