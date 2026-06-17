import sys
from typing import TYPE_CHECKING

from cat import log
from cat.context import set_app
from cat.protocols.model_context.client import MCPClients
from cat.mad_hatter.mad_hatter import MadHatter
from cat.services.factory import Registry

if TYPE_CHECKING:
    from cat.services.service import Service
    from cat.mad_hatter.plugin import Plugin


class CheshireCat:
    """
    The Cheshire Cat.

    The one ambient application per process. It is internal plumbing behind the
    `cat` package front door — user code never names it; it reaches ambient
    state with `from cat import ...`.
    """

    async def bootstrap(self, fastapi_app):
        """Cheshire Cat initialization.

        At bootstraps it loads all main components and services added by plugins.
        """

        # ^._.^

        # register this as the one ambient app for the process
        set_app(self)

        # the registry: a plain dict of service classes + a singleton cache
        self.registry = Registry(self)

        try:
            # reference to the FastAPI object
            self.fastapi_app = fastapi_app

            # instantiate MadHatter
            self.mad_hatter = MadHatter()
            self.mad_hatter.on_refresh_callbacks.append(
                self.on_mad_hatter_refresh
            )
            # Trigger plugin discovery
            await self.mad_hatter.find_plugins()

            # allows plugins to do something before cat components are loaded
            await self.mad_hatter.execute_hook("before_cat_bootstrap", None)

            # init MCP clients cache
            self.mcp_clients = MCPClients()

            # allows plugins to do something after the cat bootstrap is complete
            await self.mad_hatter.execute_hook("after_cat_bootstrap", None)

        except Exception:
            log.error("Error during CheshireCat bootstrap. Exiting.")
            sys.exit()

    async def on_mad_hatter_refresh(self):
        """Refresh CheshireCat components when MadHatter is refreshed."""

        # reindex and warmup services
        await self.refresh_registry()

        # update endpoints
        self.refresh_endpoints()

        # allow plugins to hook the refresh
        await self.mad_hatter.execute_hook("after_mad_hatter_refresh", None)

        log.welcome()

    async def refresh_registry(self):
        """Re-register core + plugin service classes (no eager construction)."""

        # avoid circular imports
        from cat.services.auths.default import DefaultAuth
        from cat.services.agents.default import DefaultAgent
        from cat.services.model_providers.openai_compatible import OpenAICompatibleProvider
        from cat.services.model_providers.default import DefaultModelProvider
        from cat.services.core_settings import CoreSettings

        # Reset registry (shutdown existing singletons and clear classes)
        await self.registry.teardown()

        # Register default services (all core-provided, one place). Core ships
        # exactly one model provider — the generic OpenAI-compatible engine; the
        # named vendor presets live in the scaffolded `llms` plugin.
        for ServiceClass in [CoreSettings, DefaultAuth, DefaultAgent, DefaultModelProvider, OpenAICompatibleProvider]:
            ServiceClass.plugin_id = "core"
            self.registry.register(ServiceClass)

        # Register all services from plugins
        for service_type, services in self.mad_hatter.service_classes.items():
            for slug, ServiceClass in services.items():
                self.registry.register(ServiceClass)

    def refresh_endpoints(self):
        """Sync plugin endpoints in the fastapi app."""

        # remove all plugin Endpoint routes from fastapi app
        routes_to_remove = []
        for route in self.fastapi_app.routes:
            # route may be a plain APIRoute (has `.endpoint`) or a nested
            # router/mount (from `@endpoint.router`) that does not
            if hasattr(getattr(route, "endpoint", None), 'plugin_id') \
                    or hasattr(route, "plugin_id"):
                routes_to_remove.append(route)
        for route in routes_to_remove:
            self.fastapi_app.routes.remove(route)

        # add the new list
        for e in self.mad_hatter.endpoints:
            self.fastapi_app.include_router(e)

        # reset openapi schema
        self.fastapi_app.openapi_schema = None

    async def get(
        self,
        type: str,
        slug: str,
        raise_error: bool = True
    ) -> "Service | None":
        """
        Get a service instance by type and slug.
        """
        return await self.registry.get(type, slug, raise_error=raise_error)

    async def get_all(self, type: str) -> "dict[str, Service]":
        """All service instances of a given type, keyed by slug."""
        return await self.registry.get_all(type)

    @property
    def plugin(self) -> "Plugin":
        """Access to the Plugin that provided this service, if any."""
        return self.mad_hatter.get_plugin()
