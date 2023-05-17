from cat.mad_hatter.decorators import hook


# Called when a user message arrives.
# Useful to edit/enrich user input (e.g. translation)
@hook(priority=0)
def before_cat_reads_message(user_message_json, cat):
    return user_message_json


# Called just before the cat recalls memories.
@hook(priority=0)
def before_cat_recalls_memories(user_message, cat):
    return None


# Called just after memories are recalled. They are stored in:
# - cat.working_memory["episodic_memories"]
# - cat.working_memory["declarative_memories"]
@hook(priority=0)
def after_cat_recalled_memories(user_message, cat):
    return None


# Hook called just before sending response to a client.
@hook(priority=0)
def before_cat_sends_message(message, cat):
    return message


# Hook called before inserting the first point in memory collection.
# This happens at first lunch and whenever `long_term_memory` is deleted.
# first_point is `langchain.Document` instance
@hook(priority=0)
def before_collection_created(first_point, cat):
    return first_point

