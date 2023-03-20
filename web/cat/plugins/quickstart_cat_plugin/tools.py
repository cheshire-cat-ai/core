from cat.mad_hatter.decorators import tool


@tool
def my_tool(tool_input):
    """This is a Tool"""
    return input + " ciao"
