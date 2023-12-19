from typing import List

from cat.mad_hatter.decorators import hook


@hook(priority=0)
def factory_allowed_llms(allowed, cat) -> List:
    """Hook to extend support of llms.

    Parameters
    ---------
    allowed : List of LLMSettings classes
        list of allowed language models 

    Returns
    -------
    supported : List of LLMSettings classes
        list of allowed language models 
    """
    return allowed
