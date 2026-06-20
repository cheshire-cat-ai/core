"""
The service registry.

A plain dictionary of registered classes — no third-party DI container, no
scopes, no instance cache. The registry owns exactly one thing: the
`type → slug → class` map (discovery). Singleton caching lives on the classes
themselves (`ServiceMeta`), and settings are loaded by each Service via
`load_settings()` — neither is the registry's concern.

`get()` just looks up a class and calls it. Construction is pure and
synchronous, and the class (not the registry) decides singleton vs fresh, so
`get(...)` and a hand-written `MyService()` build identical objects. Any async
wiring (open a client, read settings) happens lazily on first use inside the
service, not in a build-time hook.

The registry is the lazy cycle-breaker: nothing is built at import or
registration time, only on first `get()`. A provider that needs another
provider asks for it at call time, so there is no construction-order graph to
get wrong (this is why v1's `cat.x → cat.y` cycles do not return).
"""

from typing import Dict, Type, Union, TYPE_CHECKING

from cat import log

if TYPE_CHECKING:
    from cat.looking_glass.cheshire_cat import CheshireCat
    from cat.services.service import Service


class Registry:
    """Holds service classes (type → slug → class). Nothing else.

    Singleton instances are cached on the classes themselves (`ServiceMeta`), so
    the registry keeps no instance state — it is a pure discovery map.
    """

    def __init__(self, app: "CheshireCat"):
        self.app = app
        self.classes: Dict[str, Dict[str, Type["Service"]]] = {}

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

        Just "look up the class and call it" — `ServiceMeta` returns the cached
        singleton or a fresh instance per the class's `singleton` flag, so
        `get(...)` and a hand-written `ServiceClass()` agree. Settings and any
        client are pulled lazily by the service itself.
        """
        ServiceClass = self._lookup(type, slug, raise_error)
        if ServiceClass is None:
            return None
        return ServiceClass()

    async def get_all(self, type: str) -> "Dict[str, Service]":
        """All instances of a given type, keyed by slug."""
        return {slug: await self.get(type, slug) for slug in self.classes.get(type, {})}

    async def teardown(self) -> None:
        """Close every live singleton (shutdown) and clear the class map."""
        for type_map in self.classes.values():
            for ServiceClass in type_map.values():
                try:
                    await ServiceClass.refresh()
                except Exception as e:
                    log.error(f"Error during teardown of {ServiceClass.__name__}: {e}")
        self.classes = {}
