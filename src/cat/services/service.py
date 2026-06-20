"""
The Service base.

A service is a *noun you hold* — shared infrastructure resolved through the
registry. There is exactly one base class; lifecycle is a single boolean:

- `singleton = True`  (default) → built once, cached, reused.
- `singleton = False`          → built fresh per resolution (agents, which
                                  mutate run state and must not be shared).

Services reach ambient state by importing it (`from cat import embedder, user,
hook`), not through a `self.ccat` back-reference or string-keyed `requires`
injection. Settings are not loaded here either: the registry injects a typed
`self.settings` before `setup()`.
"""

from typing import TYPE_CHECKING

from pydantic import BaseModel

from cat.context import ccat

if TYPE_CHECKING:
    from cat.mad_hatter.plugin import Plugin
    from cat.protocols.model_context.client import MCPClients
    from cat.looking_glass.cheshire_cat import CheshireCat


class Service:
    """Base class for framework and plugin services."""

    service_type: str = "base"
    singleton: bool = True

    slug: str | None = None
    name: str | None = None
    description: str | None = None
    plugin_id: str | None = None

    # Typed settings, injected by the registry before setup(). None if the
    # service declares no settings.
    settings: BaseModel | None = None

    @property
    def plugin(self) -> "Plugin | None":
        """The Plugin that provided this service, if any."""
        if self.plugin_id is None:
            return None
        return ccat().mad_hatter.plugins[self.plugin_id]

    @property
    def mcp_clients(self) -> "MCPClients":
        return ccat().mcp_clients

    async def setup(self) -> None:
        """Async setup (e.g. build a client from `self.settings`). Override."""
        pass

    async def teardown(self) -> None:
        """Async cleanup for singletons on shutdown/refresh. Override."""
        pass

    @classmethod
    async def settings_schema(cls, app: "CheshireCat") -> type[BaseModel] | None:
        """
        Return the Pydantic model describing this service's settings, or None.

        Default: the nested `class Settings(BaseModel)` if declared. Override to
        build a dynamic model (e.g. an enum derived from installed plugins).
        """
        nested = getattr(cls, "Settings", None)
        if isinstance(nested, type) and issubclass(nested, BaseModel):
            return nested
        return None
