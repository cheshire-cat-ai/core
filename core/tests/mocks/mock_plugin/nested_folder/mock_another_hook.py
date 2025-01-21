from cat.mad_hatter.decorators import hook


@hook(priority=3)
def before_cat_sends_message(message, cat):
    if "Priorities" in message.text:
        message.text += " priority 3"
    return message
