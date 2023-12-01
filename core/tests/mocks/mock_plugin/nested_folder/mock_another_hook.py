from cat.mad_hatter.decorators import hook

@hook(priority=3)
def before_cat_sends_message(message, cat):
    message["content"] += " priority 3"
    return message