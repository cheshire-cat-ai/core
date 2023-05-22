"""Hooks to modify the Cat's flow of execution.

Here is a collection of methods to filter or hook into the execution pipeline.
Filters allow to edit user's input or Cat's output the text messages.
Hooks allow to intercept the flow in specific execution places,
e.g. before and after the semantic search in the memories

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
    return None


# Called after cat bootstrap
@hook(priority=0)
def after_cat_bootstrap(cat):
    return None


# Called when a user message arrives.
# Useful to edit/enrich user input (e.g. translation)
@hook(priority=0)
def before_cat_reads_message(user_message_json: dict, cat) -> dict:
    """Filters incoming user's JSON dictionary.

    Allows to edit or enrich the incoming message received from the WebSocket connection.
    This can be used to translate the user's message before feeding it to the Cat
    or to add custom keys to the JSON dictionary.

    Args:
        user_message_json: JSON dictionary with the message received from the chat stored in the *text* key.
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
def cat_recall_query(user_message, cat) -> str:
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
def after_cat_recalled_memories(memory_query_text, cat):
    return None


# Hook called just before sending response to a client.
@hook(priority=0)
def before_cat_sends_message(message, cat):
    return message
