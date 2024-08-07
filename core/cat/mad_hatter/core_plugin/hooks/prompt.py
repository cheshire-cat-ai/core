"""Hooks to modify the prompts.

Here is a collection of methods to hook the prompts components that instruct the *Agent*.

"""


from cat.mad_hatter.decorators import hook


@hook(priority=0)
def agent_prompt_prefix(prefix, cat) -> str:
    """Hook the main prompt prefix.

    Allows to edit the prefix of the *Main Prompt* that the Cat feeds to the *Agent*.
    It describes the personality of your assistant and its general task.

    The prefix is then completed with the `agent_prompt_suffix`.

    Parameters
    ----------
    prefix : str
        Main / System prompt with personality and general task to be accomplished.
    cat : StrayCat
        StrayCat instance.

    Returns
    -------
    prefix : str
        Main / System prompt.

    Notes
    -----
    The default prefix describe who the AI is and how it is expected to answer the Human.
    """

    return prefix


@hook(priority=0)
def agent_prompt_instructions(instructions: str, cat) -> str:
    """Hook the instruction prompt.

    Allows to edit the instructions that the Cat feeds to the *Agent* to select tools and forms.

    Parameters
    ----------
    instructions : str
        Instructions prompt to select tool or form.
    cat : StrayCat
        StrayCat instance.

    Returns
    -------
    instructions : str
        Instructions prompt to select tool or form

    Notes
    -----
    This prompt explains the *Agent* how to select a tool or form.

    """

    return instructions


@hook(priority=0)
def agent_prompt_suffix(prompt_suffix: str, cat) -> str:
    """Hook the main prompt suffix.

    Allows to edit the suffix of the *Main Prompt* that the Cat feeds to the *Agent*.

    The suffix is concatenated to `agent_prompt_prefix` when RAG context is used.

    Parameters
    ----------
    cat : StrayCat
        StrayCat instance.

    Returns
    -------
    prompt_suffix : str
        The suffix string to be concatenated to the *Main Prompt* (prefix).

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
