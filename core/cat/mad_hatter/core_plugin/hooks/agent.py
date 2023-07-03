"""Hooks to modify the Cat's *Agent*.

Here is a collection of methods to hook into the *Agent* execution pipeline.

"""

from typing import List

from langchain.tools.base import BaseTool
from langchain.agents import load_tools
from cat.mad_hatter.decorators import hook
from cat.log import log


@hook(priority=0)
def agent_allowed_tools(cat) -> List[BaseTool]:
    """Hook the allowed tools.

    Allows to decide which tools end up in the *Agent* prompt.

    To decide, you can filter the list of loaded tools, but you can also check the context in `cat.working_memory`
    and launch custom chains with `cat.llm`.

    Parameters
    ---------
    cat : CheshireCat
        Cheshire Cat instance.

    Returns
    -------
    tools : List[BaseTool]
        List of allowed Langchain tools.
    """

    # tools currently recalled in working memory
    recalled_tools = cat.working_memory["procedural_memories"]

    # Get the tools names only
    tools_names = [t[0].metadata["name"] for t in recalled_tools]

    # Get the LangChain BaseTool by name
    tools = [i for i in cat.mad_hatter.tools if i.name in tools_names]

    return tools


@hook(priority=0)
def before_agent_creates_prompt(input_variables, main_prompt, cat):
    """Hook to dynamically define the input variables.

    Allows to dynamically filter the input variables that end up in the main prompt by looking for which placeholders
    there are in it starting from a fixed list.

    Parameters
    ----------
    input_variables : List
        List of placeholders to look for in the main prompt.
    main_prompt: str
        String made of the prompt prefix, the agent instructions and the prompt suffix.
    cat : CheshireCat
        Cheshire Cat instance.

    Returns
    -------
    input_variables : List[str]
        List of placeholders present in the main prompt.

    """

    # Loop the input variables and check if they are in the main prompt
    input_variables = [i for i in input_variables if i in main_prompt]

    return input_variables


