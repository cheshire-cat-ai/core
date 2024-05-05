"""Hooks to modify the Cat's *Agent*.

Here is a collection of methods to hook into the *Agent* execution pipeline.

"""

from typing import List, Union, Dict

from langchain.tools.base import BaseTool
from langchain.agents import load_tools
from cat.mad_hatter.decorators import hook
from cat.log import log


@hook(priority=0)
def before_agent_starts(agent_input: Dict, cat) -> Dict:
    """Hook to read and edit the agent input

    Parameters
    --------
    agent_input: dict
        Input that is about to be passed to the agent.
    cat : CheshireCat
        Cheshire Cat instance.

    Returns
    --------
    response : Dict
        Agent Input
    """

    return agent_input


@hook(priority=0)
def agent_fast_reply(fast_reply, cat) -> Union[None, Dict]:
    """This hook is useful to shortcut the Cat response.
    If you do not want the agent to run, return the final response from here and it will end up in the chat without the agent being executed.

    Parameters
    --------
    fast_reply: dict
        Input is dict (initially empty), which can be enriched whith an "output" key with the shortcut response.
    cat : CheshireCat
        Cheshire Cat instance.

    Returns
    --------
    response : Union[None, Dict]
        Cat response if you want to avoid using the agent, or None / {} if you want the agent to be executed.
        See below for examples of Cat response

    Examples
    --------

    Example 1: can't talk about this topic
    ```python
    # here you could use cat._llm to do topic evaluation
    if "dog" in agent_input["input"]:
        return {
            "output": "You went out of topic. Can't talk about dog."
        }
    ```

    Example 2: don't remember (no uploaded documents about topic)
    ```python
    num_declarative_memories = len( cat.working_memory.declarative_memories )
    if num_declarative_memories == 0:
        return {
           "output": "Sorry, I have no memories about that."
        }
    ```
    """

    return fast_reply


@hook(priority=0)
def agent_allowed_tools(allowed_tools: List[str], cat) -> List[str]:
    """Hook the allowed tools.

    Allows to decide which tools end up in the *Agent* prompt.

    To decide, you can filter the list of tools' names, but you can also check the context in `cat.working_memory`
    and launch custom chains with `cat._llm`.

    Parameters
    ---------
    cat : CheshireCat
        Cheshire Cat instance.

    Returns
    -------
    tools : List[str]
        List of allowed Langchain tools.
    """

    return allowed_tools



