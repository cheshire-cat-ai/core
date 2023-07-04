from cat.mad_hatter.decorators import hook, tool


@tool(return_direct=True)
def random_idea(topic, cat):
    """Use to produce random ideas. Input is the topic."""

    return f"A random idea about {topic} :)"
