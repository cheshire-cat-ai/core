from cat.decorators import hook, tool


# TODO: allow plugin devs to store stuff in the context
@hook(priority=10)
def get_language_model(cat):
    mylm = {}
    return mylm


@tool
def mytool(inp):
    """use this tool to fuck around"""
    return "I AM THE CAAAAAAT"


@hook
def before_inserting_into_memory(stuff):
    return stuff


# @prompt
