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

    # Get the User's input
    user_input = cat.working_memory["user_message_json"]["text"]

    # Embed the user's input to query the procedural memory with it
    query_embedding = cat.embedder.embed_query(user_input)

    # Check if procedural memory is enabled
    prompt_settings = cat.working_memory["user_message_json"]["prompt_settings"]

    if prompt_settings["use_procedural_memory"]:
        # Make semantic search in the procedural memory to retrieve the name of the most suitable tools
        embedded_tools = cat.memory.vectors.procedural.recall_memories_from_embedding(
            query_embedding, k=5, threshold=0.6
        )
        # Get the tools names only
        tools_names = [t[0].metadata["name"] for t in embedded_tools]

        # Get the LangChain BaseTool by name
        tools = [i for i in cat.mad_hatter.tools if i.name in tools_names]

    else:
        tools=[]
    
    # log(tools, "ERROR")

    # Add LangChain default tools
    # Full list here: https://python.langchain.com/en/latest/modules/agents/tools.html
    #default_tools_name = ["llm-math"]  # , "python_repl", "terminal"]
    #default_tools = load_tools(default_tools_name, llm=cat.llm)

    #allowed_tools = tools + default_tools

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


