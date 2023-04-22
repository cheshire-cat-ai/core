from cat.mad_hatter.decorators import hook

# Hook called just before sending response to a client.
@hook(priority=0)
def before_returning_response_to_user(response, cat):
    return response

