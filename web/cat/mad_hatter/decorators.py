# We use the @tool decorator directly from langchain, 'as is'.
# The plugin system imports it from here (cat.decorators module), as it will be possible to extend it later on
# from langchain.agents import tool as langchain_tool
from cat.utils import log


def hook(func):
    def cat_hook_wrapper(*args, **kwargs):
        log(func)
        return func(*args, **kwargs)

    return cat_hook_wrapper


def tool(func):
    #    @langchain_tool # TODO: use directly the langchain @tool decorator, or wrap it somehow
    def cat_tool_wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return cat_tool_wrapper
