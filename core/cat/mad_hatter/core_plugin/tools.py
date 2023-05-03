from datetime import datetime

from cat.mad_hatter.decorators import tool


@tool
def get_the_time(tool_input, cat):
    """Retrieves current time and clock. Input is always None."""

    return str(datetime.now())
