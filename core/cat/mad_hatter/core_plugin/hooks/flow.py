"""Hooks to modify the Cat's flow of execution.

Here is a collection of methods to hook into the execution pipeline.
These hooks allow to intercept the flow in specific execution places,
e.g. before and after the semantic search in the memories;
or to edit and enhance user's and Cat's messages.

Typical usage example:

  from cat.mad_hatter.decorators import tool, hook

  @hook(priority=1)
  def name_of_the_hook_to_overridden(use-equal-parameters):
    **custom execution**
    return custom_output
"""

from cat.mad_hatter.decorators import hook


# Called before cat bootstrap
@hook(priority=0)
def before_cat_bootstrap(cat):
    """Hook into the Cat start up.

    Bootstrapping is the process of loading the plugins, the natural language objects (e.g. the LLM),
    the memories, the *Agent Manager* and the *Rabbit Hole*. This hook allows to intercept such process and is executed
    in the middle of plugins and natural language objects loading.
    This can be used to set or store variables to be propagated to subsequent loaded objects.

    Args:
        cat: Cheshire Cat instance.
    """
    return None


# Called after cat bootstrap
@hook(priority=0)
def after_cat_bootstrap(cat):
    """Hook into the end of the Cat start up.

    Bootstrapping is the process of loading the plugins, the natural language objects (e.g. the LLM),
    the memories, the *Agent Manager* and the *Rabbit Hole*. This hook allows to intercept the end of such process
    and is executed right after the Cat has finished loading its components.
    This can be used to set or store variables to be shared further in the pipeline.

    Args:
        cat: Cheshire Cat instance.
    """
    return None


# Called when a user message arrives.
# Useful to edit/enrich user input (e.g. translation)
@hook(priority=0)
def before_cat_reads_message(user_message_json: dict, cat) -> dict:
    """Hook the incoming user's JSON dictionary.

    Allows to edit or enrich the incoming message received from the WebSocket connection.
    This can be used to translate the user's message before feeding it to the Cat
    or to add custom keys to the JSON dictionary.

    Args:
        user_message_json: JSON dictionary with the message received from the chat. The user's message
        is stored in the "*text*" key.
        cat: Cheshire Cat instance to exploit the Cat's methods.

    Returns:
        Edited JSON dictionary that will be fed to the Cat. For
        example:

        {"text": "Hello Cheshire Cat!",
        "custom_key": True}

        "custom_key" is a newly added key to the JSON that stores a boolean that can be used further in
        the pipeline or in a plugin.

    """
    return user_message_json


# Called just before the cat recalls memories.
@hook(priority=0)
def before_cat_recalls_memories(user_message: str, cat) -> None:
    """Hook into semantic search in memories.

    Allows to intercept when the Cat queries the memories using the embedded user's input.
    The hook is executed just before the Cat searches for the meaningful context in both memories
    and stores it in the Working Memory.

    Args:
        user_message: string with the text received from the user. This is used as a query to search into memories.
        cat: Cheshire Cat instance to exploit the Cat's methods.
    """
    return None


# What is the input to recall memories?
# Here you can do HyDE embedding, condense recent conversation or condition recall query on something else important to your AI
@hook(priority=0)
def cat_recall_query(user_message: str, cat) -> str:
    """Hook the Hypothetical Document Embedding (HyDE) search query.

    HyDE strategy exploits the user's message to generate a hypothetical answer. This
    is applied to recall the relevant context from the memory. This hook allows to edit
    the user's message. As a result, context retrieval can be conditioned enhancing the user's message.

    Args:
        user_message: string with the text received from the user.
        cat: Cheshire Cat instance to exploit the Cat's methods.

    Returns:
        Edited string to be used for context retrieval in memory. The
        returned string is further stored in the Working Memory at
        `cat.working_memory["memory_query"]`
    """
    # example 1: HyDE embedding
    # return cat.hypothetis_chain.run(user_message)

    # example 2: Condense recent conversation
    # TODO

    # here we just return the latest user message as is
    return user_message


# Called just after memories are recalled. They are stored in:
# - cat.working_memory["episodic_memories"]
# - cat.working_memory["declarative_memories"]
@hook(priority=0)
def after_cat_recalled_memories(memory_query_text: str, cat):
    """Hook into semantic search after the memory retrieval.

    Allows to intercept the recalled memories right after these are stored in the Working Memory.
    According to the user's input, the relevant context is saved in `cat.working_memory["episodic_memories"]`
    and `cat.working_memory["declarative_memories"]`. At this point,
    this hook is executed to edit the search query.

    Args:
        memory_query_text: string used to query both *episodic* and *declarative* memories.
        cat: Cheshire Cat instance to exploit the Cat's methods.
    """
    return None


# Hook called just before sending response to a client.
@hook(priority=0)
def before_cat_sends_message(message, cat):
    """Hook the outgoing Cat's message.

    Allows to edit the JSON dictionary that will be sent to the client via WebSocket connection.
    This hook can be used to edit the message sent to the user or to add keys to the dictionary.

    Args:
        message: JSON dictionary to be sent to WebSocket client.
        cat: Cheshire Cat instance to exploit the Cat's methods.

    Returns:
        Edited JSON dictionary with the Cat's answer. Default
        to:

        {
            "error": False,

            "type": "chat",

            "content": cat_message["output"],

            "why": {

            "input": cat_message["input"],

            "output": cat_message["output"],

            "intermediate_steps": cat_message["intermediate_steps"],

            "memory": {

            "vectors": {

            "episodic": episodic_report,

            "declarative": declarative_report
            }
            },
            },
        }
    """
    return message
