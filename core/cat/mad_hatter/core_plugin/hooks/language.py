from typing import List

from cat.mad_hatter.decorators import hook


@hook(priority=0)
def supported_llms_list(supported,cat) -> List:
    """Hook to extend support of llms.

    Parameters
    ---------
    supported : List of pydantic class
        list of supported_language_models 

    Returns
    -------
    supported : List of pydantic class
        list of supported language models 
    """
    return supported
