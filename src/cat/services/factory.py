import asyncio
from typing import List, Dict, Type, Union, TYPE_CHECKING
from fastapi import Request
from punq import Container, Scope

from cat import log

if TYPE_CHECKING:
    from cat.looking_glass.cheshire_cat import CheshireCat
    from cat.services.service import Service


class ServiceFactory:

    def __init__(self, ccat: "CheshireCat"):
        self.ccat = ccat
        self.container = Container()
        self.class_index: Dict[str, Dict[str, Type["Service"]]] = {}
        self._setup_locks: Dict[int, asyncio.Lock] = {}

    def register(self, ServiceClass: Type["Service"]):
        if ServiceClass.lifecycle == "singleton":
            self.container.register(
                ServiceClass,
                scope=Scope.singleton,
            )
        else:
            self.container.register(ServiceClass)

        type, slug = ServiceClass.service_type, ServiceClass.slug
        if type not in self.class_index:
            self.class_index[type] = {}
        self.class_index[type][slug] = ServiceClass

    async def teardown(self):
        # stop singletons
        for instance in self.container._singletons.values():
            try:
                await instance.teardown()
            except Exception as e:
                log.error(f"Error during teardown of {instance}: {e}")
        # new container
        self.container = Container()
        self.class_index = {}
        self._setup_locks = {}

    async def get(
        self,
        type: str,
        slug: str,
        request: Request | None = None,
        raise_error: bool = True
    ) -> Union["Service", None]:
        """
        Get a service instance by type and slug.

        Parameters
        ----------
        type : str
            The type of service (e.g. "agents", "auths", "directives").
        slug : str
            The slug identifier for the service (e.g. "my_agent", "graph_memory").
        request : Request, optional
            The FastAPI request object, required for request-scoped services.
        raise_error : bool, optional
            Whether to raise an error if the service is not found. Default is True.

        Returns
        -------
        Service | None
            The service instance if found, None otherwise.
        """
        ServiceClass = self._resolve_service_class(type, slug, raise_error)
        if ServiceClass is None:
            return None

        service = self.container.resolve(ServiceClass)
        self._inject_context(service, request)
        await self._resolve_dependencies(service, request)
        await self._setup_service(service, type, slug)

        return service

    def _resolve_service_class(
        self,
        type: str,
        slug: str,
        raise_error: bool
    ) -> Union[Type["Service"], None]:
        """Lookup ServiceClass from class_index."""
        try:
            return self.class_index[type][slug]
        except Exception:
            if raise_error:
                raise Exception(f"Service of type '{type}' and slug '{slug}' not found")
            return None

    def _inject_context(self, service: "Service", request: Request | None) -> None:
        """Inject CheshireCat reference and request for request-scoped services."""
        if not hasattr(service, 'ccat'):
            service.ccat = self.ccat
        if service.lifecycle == "request":
            if request is None:
                raise Exception(
                    f"Request object must be provided for request-scoped service {service.__class__.__name__}")
            service.request = request

    async def _resolve_dependencies(self, service: "Service", request: Request | None) -> None:
        """Resolve and inject service dependencies from 'requires' dict."""
        requires = getattr(service.__class__, 'requires', {})
        for service_type, slugs in requires.items():
            if isinstance(slugs, str):
                resolved = await self.get(service_type, slugs, request=request, raise_error=False)
            else:
                resolved = []
                for s in slugs:
                    instance = await self.get(service_type, s, request=request, raise_error=False)
                    if instance:
                        resolved.append(instance)
            setattr(service, service_type, resolved)

    async def refresh(self, type: str, slug: str) -> None:
        """Tear down and re-setup a single singleton service."""
        ServiceClass = self._resolve_service_class(type, slug, raise_error=True)

        # Find the singleton instance in the container
        for key, instance in self.container._singletons.items():
            if isinstance(instance, ServiceClass):
                await instance.teardown()
                if hasattr(instance, '_setup_done'):
                    del instance._setup_done
                # Re-setup will happen on next get() call
                break

    async def _setup_service(self, service: "Service", type: str, slug: str) -> None:
        """Setup service with singleton locking or direct call for request-scoped."""

        try:
            if service.lifecycle == "singleton":
                # Fast path: check without lock first (double-checked locking pattern)
                if not hasattr(service, '_setup_done'):
                    service_id = id(service)
                    if service_id not in self._setup_locks:
                        self._setup_locks[service_id] = asyncio.Lock()

                    # Acquire lock only if setup not done
                    async with self._setup_locks[service_id]:
                        # Check again inside lock to handle race conditions
                        if not hasattr(service, '_setup_done'):
                            await service.setup()
                            service._setup_done = True
            else:
                # Request-scoped services are fresh instances, always setup
                await service.setup()
        except Exception as e:
            log.error(f"Error during setup of {service}: {e}")
