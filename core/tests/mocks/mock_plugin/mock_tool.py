from cat.mad_hatter.decorators import tool


@tool(return_direct=True)
def mock_tool(topic, cat):
    """Used to test mock tools. Input is the topic."""

    return f"A mock about {topic} :)"
