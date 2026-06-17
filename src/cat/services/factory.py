"""
The service registry.

A plain dictionary of registered classes plus a singleton-instance cache — no
third-party DI container, no scopes, no double-checked locking. `get()`
resolves a class, injects its typed settings, runs `setup()`, and caches it if
it is a singleton. Non-singletons are built fresh every time.

The registry is the lazy cycle-breaker: nothing is built at import or
registration time, only on first `get()`. A provider that needs another
provider asks for it at call time, so there is no construction-order graph to
get wrong (this is why v1's `cat.x → cat.y` cycles do not return).
"""

from typing import Dict, Type, Union, TYPE_CHECKING

from cat import log
from cat.settings import settings as settings_manager

if TYPE_CHECKING:
    from cat.looking_glass.cheshire_cat import CheshireCat
    from cat.services.service import Service


class Registry:
    """Holds service classes (type → slug → class) and a singleton cache."""

    def __init__(self, app: "CheshireCat"):
        self.app = app
        self.classes: Dict[str, Dict[str, Type["Service"]]] = {}
        self.live: Dict[tuple[str, str], "Service"] = {}

    def register(self, ServiceClass: Type["Service"]) -> None:
        type, slug = ServiceClass.service_type, ServiceClass.slug
        self.classes.setdefault(type, {})[slug] = ServiceClass

    def _lookup(
        self, type: str, slug: str, raise_error: bool
    ) -> Union[Type["Service"], None]:
        try:
            return self.classes[type][slug]
        except KeyError:
            if raise_error:
                raise Exception(f"Service of type '{type}' and slug '{slug}' not found")
            return None

    async def get(
        self, type: str, slug: str, raise_error: bool = True
    ) -> Union["Service", None]:
        """
        Resolve a service instance by type and slug.

        Singletons are built once and cached; non-singletons are built fresh.
        On build, the typed settings are loaded and injected as `self.settings`
        before `setup()` runs.
        """
        ServiceClass = self._lookup(type, slug, raise_error)
        if ServiceClass is None:
            return None

        if ServiceClass.singleton and (type, slug) in self.live:
            return self.live[(type, slug)]

        service = ServiceClass()
        service.settings = await settings_manager.load(ServiceClass, self.app)

        try:
            await service.setup()
        except Exception as e:
            log.error(f"Error during setup of {ServiceClass.__name__}: {e}")

        if ServiceClass.singleton:
            self.live[(type, slug)] = service

        return service

    async def get_all(self, type: str) -> "Dict[str, Service]":
        """All instances of a given type, keyed by slug."""
        return {slug: await self.get(type, slug) for slug in self.classes.get(type, {})}

    async def refresh(self, type: str, slug: str) -> None:
        """Tear down a cached singleton and drop it; next get() rebuilds it."""
        instance = self.live.pop((type, slug), None)
        if instance is not None:
            try:
                await instance.teardown()
            except Exception as e:
                log.error(f"Error during teardown of {type}:{slug}: {e}")

    async def teardown(self) -> None:
        """Tear down all singletons and clear the registry."""
        for instance in self.live.values():
            try:
                await instance.teardown()
            except Exception as e:
                log.error(f"Error during teardown of {instance}: {e}")
        self.classes = {}
        self.live = {}
