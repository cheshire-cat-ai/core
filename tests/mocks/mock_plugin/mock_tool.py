from cat.mad_hatter.decorators import tool


@tool
def mock_tool(topic, caller):
    """Used to test mock tools. Input is the topic."""

    return f"A mock about {topic} :)"
