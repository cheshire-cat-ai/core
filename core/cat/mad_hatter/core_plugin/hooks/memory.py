from cat.mad_hatter.decorators import hook


# Hook called before inserting the first point in memory collection.
# This happens at first lunch and whenever `long_term_memory` is deleted.
# first_point is `langchain.Document` instance
@hook(priority=0)
def before_collection_created(first_point, cat):
    return first_point
