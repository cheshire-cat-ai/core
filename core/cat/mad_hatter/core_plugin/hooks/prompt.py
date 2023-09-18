"""Hooks to modify the prompts.

Here is a collection of methods to hook the prompts components that instruct the *Agent*.

"""

import time
from typing import List, Dict

from cat.mad_hatter.decorators import hook


@hook(priority=0)
def agent_prompt_prefix(prefix, cat) -> str:
    """Hook the main prompt prefix.

    Allows to edit the prefix of the *Main Prompt* that the Cat feeds to the *Agent*.

    The prefix is then composed with two other prompts components, i.e. the `agent_prompt_instructions`
    and the `agent_prompt_suffix`.

    Parameters
    ----------
    cat : CheshireCat
        Cheshire Cat instance.

    Returns
    -------
    prefix : str
        The prefix string to be composed with the other two components to make up the *Main Prompt*.

    Notes
    -----
    The default prefix describe who the AI is and how it is expected to answer the Human.
    The next part of the prompt (generated form the *Agent*) contains the list of available Tools.

    """

    return prefix


@hook(priority=0)
def agent_prompt_instructions(instructions: str, cat) -> str:
    """Hook the instruction prompt.

    Allows to edit the instructions that the Cat feeds to the *Agent*.

    The instructions are then composed with two other prompt components, i.e. `agent_prompt_prefix`
    and `agent_prompt_suffix`.

    Parameters
    ----------
    cat : CheshireCat
        Cheshire Cat instance.

    Returns
    -------
    instructions : str
        The string with the set of instructions informing the *Agent* on how to format its reasoning to select a
        proper tool for the task at hand.

    Notes
    -----
    This prompt explains the *Agent* how to format its chain of reasoning when deciding when and which tool to use.
    Default prompt splits the reasoning in::

        - Thought: Yes/No answer to the question "Do I need to use a tool?";

        - Action: a tool chosen among the available ones;

        - Action Input: input to be passed to the tool. This is inferred as explained in the tool docstring;

        - Observation: description of the result (which is the output of the @tool decorated function found in plugins).

    """

    return instructions


@hook(priority=0)
def agent_prompt_suffix(prompt_suffix: str, cat) -> str:
    """Hook the main prompt suffix.

    Allows to edit the suffix of the *Main Prompt* that the Cat feeds to the *Agent*.

    The suffix is then composed with two other prompts components, i.e. the `agent_prompt_prefix`
    and the `agent_prompt_instructions`.

    Parameters
    ----------
    cat : CheshireCat
        Cheshire Cat instance.

    Returns
    -------
    suffix : str
        The suffix string to be composed with the other two components that make up the *Main Prompt*.

    Notes
    -----
    The default suffix has a few placeholders:
    - {episodic_memory} provides memories retrieved from *episodic* memory (past conversations)
    - {declarative_memory} provides memories retrieved from *declarative* memory (uploaded documents)
    - {chat_history} provides the *Agent* the recent conversation history
    - {input} provides the last user's input
    - {agent_scratchpad} is where the *Agent* can concatenate tools use and multiple calls to the LLM.

    """

    return prompt_suffix
