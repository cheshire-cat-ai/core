from datetime import datetime

from cat.mad_hatter.decorators import tool


@tool
def get_the_time(tool_input, cat):
    """Replies to "what time is it", "get the clock" and similar questions. Input is always None."""

    return str(datetime.now())


