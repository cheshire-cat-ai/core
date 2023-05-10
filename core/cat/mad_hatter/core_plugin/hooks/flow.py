from cat.mad_hatter.decorators import hook


# Hook called when a user message arrives.
# Useful to edit/enrich user input (e.g. translation)
@hook(priority=0)
def user_message_just_arrived(user_message_json, cat):
    user_message_json["text"] = "what time is it?"
    return user_message_json


# Hook called just before sending response to a client.
@hook(priority=0)
def before_returning_response_to_user(response, cat):
    return response


# Hook called just before of inserting documents in vector memory
@hook(priority=0)
def rabbit_hole_before_inserting_doc_in_vector_memory(doc, cat):
    return doc
