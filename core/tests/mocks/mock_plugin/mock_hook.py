from cat.mad_hatter.decorators import hook

@hook(priority=2)
def before_cat_sends_message(message, cat):
    if "Priorities" in message.content:
        message.content += " priority 2"
    return message