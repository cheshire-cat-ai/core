"""Hooks to modify the Cat's *Agent*.

Here is a collection of methods to hook into the *Agent* execution pipeline.

"""

from typing import List

from langchain.tools.base import BaseTool
from langchain.agents import load_tools
from cat.mad_hatter.decorators import hook


@hook(priority=0)
def agent_allowed_tools(cat) -> List[BaseTool]:
    """Hook the allowed tools.

    Allows to decide which tools end up in the *Agent* prompt.

    To decide, you can filter the list of loaded tools, but you can also check the context in `cat.working_memory`
     and launch custom chains with `cat.llm`.

    Args:
        cat: Cheshire Cat instance.

    Returns:
        List of allowed tools.
    """

    # add to plugin defined tools, also some default tool included in langchain
    # see complete list here: https://python.langchain.com/en/latest/modules/agents/tools.html
    default_tools_name = ["llm-math"]  # , "python_repl", "terminal"]
    default_tools = load_tools(default_tools_name, llm=cat.llm)

    allowed_tools = cat.mad_hatter.tools + default_tools

    return allowed_tools


@hook(priority=0)
def before_agent_creates_prompt(input_variables, main_prompt, cat):
    """Hook to dynamically define the input variables.

    Allows to dynamically filter the input variables that end up in the main prompt by looking for which placeholders
    there are in it starting from a fixed list.

    Args:
        input_variables: list of placeholders to look for in the main prompt
        main_prompt: string made of the prompt prefix, the agent instructions and the prompt suffix
        cat: Cheshire Cat instance

    Returns:
        list of placeholders present in the main prompt.

    """

    # Loop the input variables and check if they are in the main prompt
    input_variables = [i for i in input_variables if i in main_prompt]

    return input_variables


