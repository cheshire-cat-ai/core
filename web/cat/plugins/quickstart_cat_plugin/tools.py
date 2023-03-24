from cat.mad_hatter.decorators import tool


@tool
def my_shoes(tool_input):
    """Retrieves information about shoes"""
    return "I own Nike air MAXXXX"


@tool
def my_shoes_color(tool_input):
    """Retrieves color of shoes"""
    return "pink shoes"
