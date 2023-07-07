"""Hooks to modify the Cat's *Agent*.

Here is a collection of methods to hook into the *Agent* execution pipeline.

"""

from typing import List, Union, Dict

from langchain.tools.base import BaseTool
from langchain.agents import load_tools
from cat.mad_hatter.decorators import hook
from cat.log import log


@hook(priority=0)
def before_agent_starts(agent_input, cat) -> Union[None, Dict]:
    """Hook before the agent starts.

    This hook is useful to shortcut the Cat response.
    If you do not want the agent to run, return the final response from here and it will edn up in the chat without the agent being executed.

    Parameters
    --------
    agent_input: Dict
        Input that is about to be passed to the agent.
    cat : CheshireCat
        Cheshire Cat instance.

    Returns
    --------
    response : Dict
        Cat response if you want to avoid using the agent, or None if you want the agent to be executed.
        See hook's code for example of Cat response

    Examples
    --------
    # Example 1: can't talk about this topic
    >>> if "dog" in agent_input["input"]: # here you can use cat.llm to do topic evaluation
    >>>    return {
    >>>        "output": "You went out of topic. Can't talk about dog."
    >>>    }

    # Example 2: don't remember (no uploaded documents about topic)
    >>> num_declarative_memories = len( cat.working_memory["declarative_memories"] )
    >>> log(num_declarative_memories, "ERROR")
    >>> if num_declarative_memories == 0:
    >>>    return {
    >>>        "output": "Sorry, I have no memories about that."
    >>>    }
    """

    return None


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


