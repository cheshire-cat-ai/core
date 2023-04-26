from datetime import datetime

from cat.mad_hatter.decorators import tool


@tool
def get_the_time(tool_input, cat):
    """
    Retrieves current time and clock. Input is always None.

    :param tool_input: Tool Input
    :type tool_input: tool_input
    :param cat: Cat
    :type cat: cat
    :return: datetime.now
    :rtype: str
    """
    return str(datetime.now())
