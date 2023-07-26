from cat.mad_hatter.decorators import hook

@hook(priority=2)
def before_cat_sends_message(message, cat):
    message["content"] = "Lazy cat says: " + message["content"]
    return message