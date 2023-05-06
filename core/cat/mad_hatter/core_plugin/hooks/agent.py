from langchain.agents import load_tools
from cat.mad_hatter.decorators import hook


@hook(priority=0)
def get_allowed_tools(tools, cat):
    """Decide which tools end up in the agent prompt. To decide you can filter the list of loaded tools,
        but you can also check the context in cat.working_memory and launch custom chains with cat.llm.

    Args:
        tools: list of @tool functions extracted from plugins
        cat: instance of the cat

    Returns:
        list of allowed tools
    """

    # add to plugin defined tools, also some default tool included in langchain
    # see complete list here: https://python.langchain.com/en/latest/modules/agents/tools.html
    default_tools_name = ["llm-math"]  # , "python_repl", "terminal"]
    default_tools = load_tools(default_tools_name, llm=cat.llm)

    allowed_tools = tools + default_tools

    return allowed_tools
