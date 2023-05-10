from cat.mad_hatter.decorators import hook


# Hook called just before of inserting documents in vector memory
@hook(priority=0)
def before_rabbithole_insert_memory(doc, cat):
    return doc
