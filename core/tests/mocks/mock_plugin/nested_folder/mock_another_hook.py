from cat.mad_hatter.decorators import hook

@hook(priority=3)
def before_cat_sends_message(message, cat):
    if "Priorities" in message.content:
        message.content += " priority 3"
    return message