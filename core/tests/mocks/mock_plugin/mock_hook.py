from cat.mad_hatter.decorators import hook


@hook(priority=2)
def before_cat_sends_message(message, cat):
    if "Priorities" in message.text:
        message.text += " priority 2"
    return message
