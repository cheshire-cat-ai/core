"""Hooks to modify the Cat's *Agent*.

Here is a collection of methods to hook into the *Agent* execution pipeline.

Example:

    from cat.mad_hatter.decorators import tool, hook

    @hook(priority=1)

    def name_of_the_hook_to_overridden(use-equal-parameters):
        **custom execution**

        return custom_output

"""

from typing import List

from langchain.tools.base import BaseTool
from langchain.agents import load_tools
from cat.mad_hatter.decorators import hook


@hook(priority=0)
def agent_allowed_tools(tools: List[BaseTool], cat) -> List[BaseTool]:
    """Hook the allowed tools.

    Decide which tools end up in the *Aget* prompt. To decide, you can filter the list of loaded tools,
    but you can also check the context in `cat.working_memory` and launch custom chains with `cat.llm`.

    Args:
        tools: list of @tool functions extracted from the plugins
        cat: instance of the Cat

    Returns:
        List of allowed tools
    """

    # add to plugin defined tools, also some default tool included in langchain
    # see complete list here: https://python.langchain.com/en/latest/modules/agents/tools.html
    default_tools_name = ["llm-math"]  # , "python_repl", "terminal"]
    default_tools = load_tools(default_tools_name, llm=cat.llm)

    allowed_tools = tools + default_tools

    return allowed_tools
