# TODO: this is the main config for the cat.
# TODO: should be loaded from a DB at startup
# TODO: can be overridden from plugins
# TODO: can be overridden from REST API

from pydantic import BaseSettings
from cat.config.llm import SUPPORTED_LANGUAGE_MODELS


class CheshireCatSettings(BaseSettings):
    supported_language_models = SUPPORTED_LANGUAGE_MODELS
    chosen_language_model = 0
    chosen_embedder = 0
    verbose: bool = True
