from typing import List

from cat.factory.llm import LLMSettings
from cat.factory.embedder import EmbedderSettings
from cat.factory.auth_handler import AuthHandlerConfig
from cat.mad_hatter.decorators import hook


@hook(priority=0)
def factory_allowed_llms(allowed: List[LLMSettings], cat) -> List:
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


@hook(priority=0)
def factory_allowed_embedders(allowed: List[EmbedderSettings], cat) -> List:
    """Hook to extend list of supported embedders.

    Parameters
    ---------
    allowed : embedder of EmbedderSettings classes
        list of allowed embedders

    Returns
    -------
    supported : List of EmbedderSettings classes
        list of allowed embedders
    """
    return allowed


@hook(priority=0)
def factory_allowed_auth_handlers(allowed: List[AuthHandlerConfig], cat) -> List:
    """Hook to extend list of supported auth_handlers.

    Parameters
    ---------
    allowed : List of AuthHandlerConfig classes
        list of allowed auth_handlers

    Returns
    -------
    supported : List of AuthHandlerConfig classes
        list of allowed auth_handlers
    """

    # TODOAUTH: documentation links to language.py must be moved to factory.py
    return allowed
