from datetime import datetime

from cat.mad_hatter.decorators import tool


@tool(examples=["what time is it", "get the time"])
def get_the_time(tool_input, cat):
    """Useful to get the current time when asked. Input is always None."""

    return f"The current time is {str(datetime.now())}"
