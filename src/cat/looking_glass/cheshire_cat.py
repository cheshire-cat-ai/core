import sys
from typing import TYPE_CHECKING

from cat import log
from cat.protocols.model_context.client import MCPClients
from cat.mad_hatter.mad_hatter import MadHatter
from cat.services.factory import ServiceFactory

if TYPE_CHECKING:
    from cat.services.service import Service
    from cat.mad_hatter.plugin import Plugin


class CheshireCat:
    """
    The Cheshire Cat.

    Main class that manages the whole AI application.
    It contains references to all the main modules and is responsible for application bootstrapping.
    """

    async def bootstrap(self, fastapi_app):
        """Cheshire Cat initialization.

        At bootstraps it loads all main components and services added by plugins.
        """

        # ^._.^

        # service factory for managing service lifecycle
        self.factory = ServiceFactory(self)

        try:
            # reference to the FastAPI object
            self.fastapi_app = fastapi_app
            # reference to the cat in fastapi state
            fastapi_app.state.ccat = self

            # instantiate MadHatter
            self.mad_hatter = MadHatter()
            self.mad_hatter.on_refresh_callbacks.append(
                self.on_mad_hatter_refresh
            )
            # Preinstall plugins if needed
            await self.mad_hatter.preinstall_plugins()
            # Trigger plugin discovery
            await self.mad_hatter.find_plugins()
            
            # allows plugins to do something before cat components are loaded
            await self.mad_hatter.execute_hook(
                "before_cat_bootstrap", None, caller=self
            )

            # init MCP clients cache
            self.mcp_clients = MCPClients()

            # allows plugins to do something after the cat bootstrap is complete
            await self.mad_hatter.execute_hook(
                "after_cat_bootstrap", None, caller=self
            )

        except Exception:
            log.error("Error during CheshireCat bootstrap. Exiting.")
            sys.exit()

    async def on_mad_hatter_refresh(self):
        """Refresh CheshireCat components when MadHatter is refreshed."""

        
        # reindex and warmup services
        await self.refresh_factory()

        # update endpoints
        self.refresh_endpoints()

        # allow plugins to hook the refresh
        await self.mad_hatter.execute_hook(
            "after_mad_hatter_refresh", None, caller=self
        )

        log.welcome()

    async def refresh_factory(self):
        """Warmup long lived services."""

        # avoid circular imports
        from cat.services.auths.default import DefaultAuth
        from cat.services.agents.default import DefaultAgent
        from cat.services.model_providers.default import DefaultModelProvider
        from cat.services.core_settings import CoreSettings

        # Reset factory (shutdown existing services and clear registry)
        await self.factory.teardown()

        # Register default services
        for ServiceClass in [CoreSettings, DefaultAuth, DefaultModelProvider, DefaultAgent]:
            ServiceClass.plugin_id = "core"
            self.factory.register(ServiceClass)

        # Register all services from plugins
        for service_type, services in self.mad_hatter.service_classes.items():
            for slug, ServiceClass in services.items():
                self.factory.register(ServiceClass)

    def refresh_endpoints(self):
        """Sync plugin endpoints in the fastapi app."""

        # remove all plugin Endpoint routes from fastapi app
        routes_to_remove = []
        for route in self.fastapi_app.routes:
            if hasattr(route.endpoint, 'plugin_id'):
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
        request=None,
        raise_error: bool = True
    ) -> "Service | None":
        """
        Get a service instance by type and slug.
        Delegates to the internal factory.

        Parameters
        ----------
        type : str
            The type of service (e.g. "agents", "auths", "model_providers").
        slug : str
            The slug identifier for the service.
        request : Request, optional
            The FastAPI request object, required for request-scoped services.
        raise_error : bool, optional
            Whether to raise an error if the service is not found. Default is True.

        Returns
        -------
        Service | None
            The service instance if found, None otherwise.
        """
        return await self.factory.get(type, slug, request=request, raise_error=raise_error)

    async def get_all(self, type: str) -> "dict[str, Service]":
        """
        Get all service instances of a given type as a dictionary slug -> instance.

        Parameters
        ----------
        type : str
            The type of service (e.g. "agents", "auths", "model_providers").

        Returns
        -------
        dict[str, Service]
            Dictionary of service instances keyed by slug.
        """
        result = {}
        for slug in self.factory.class_index.get(type, {}):
            result[slug] = await self.factory.get(type, slug)
        return result

    @property
    def plugin(self) -> "Plugin":
        """Access to the Plugin that provided this service, if any."""
        return self.mad_hatter.get_plugin()

