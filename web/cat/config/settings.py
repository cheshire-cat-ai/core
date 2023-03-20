# TODO: this is the main config for the cat.
# TODO: should be loaded from a DB at startup
# TODO: can be overridden from plugins
# TODO: can be overridden from REST API

from pydantic import BaseSettings

# from cat.llm import


class CheshireCatSettings(BaseSettings):
    verbose: bool = True
