from datetime import datetime

from cat.mad_hatter.decorators import tool


@tool
def get_the_time(tool_input):
    """Retrieves current time and clock. Input is always None."""
    return str(datetime.now())


@tool
def my_shoes_color(tool_input):
    """Retrieves color of shoes. Input is always None."""
    return "pink shoes"
