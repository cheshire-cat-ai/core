from cat.mad_hatter.decorators import hook


# Hook called just before sending response to a client.
@hook(priority=0)
def before_returning_response_to_user(response, cat):
    return response


# Hook called just before of inserting documents in vector memory
@hook(priority=0)
def rabbit_hole_before_inserting_doc_in_vector_memory(doc, cat):
    return doc
