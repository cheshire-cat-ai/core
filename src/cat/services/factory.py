"""
The service registry.

A plain dictionary of registered classes plus a singleton-instance cache — no
third-party DI container, no scopes, no double-checked locking. The registry
owns exactly two things: the `type → slug → class` map (discovery), and the
lifecycle of singleton instances (build-once cache + `teardown`). Settings are
*not* its concern — every Service loads its own via `load_settings()`.

`get()` resolves a class, constructs it, and caches it if it is a singleton.
Construction is pure and synchronous, so `get(...)` and a hand-written
`MyService()` build identical objects — `get` only adds caching. Any async
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
        Construction is pure — settings and any client are pulled lazily by the
        service itself, not injected here.
        """
        ServiceClass = self._lookup(type, slug, raise_error)
        if ServiceClass is None:
            return None

        if ServiceClass.singleton and (type, slug) in self.live:
            return self.live[(type, slug)]

        service = ServiceClass()

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
