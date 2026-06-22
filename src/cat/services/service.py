"""
The Service base.

A service is a object resolved through the internal cat
registry. There is exactly one base class; lifecycle is a single boolean:

- `singleton = True`  (default) → built once, cached, reused.
- `singleton = False`          → built fresh per resolution (agents, which
                                  mutate run state and must not be shared).

Services reach ambient state by importing it (`from cat import embedder, user,
hook`), not through a `self.ccat` back-reference or string-keyed injection.

Settings live on the service itself: declare a nested `class Settings(BaseModel)`
(or override `settings_schema()` for a dynamic one) and read the current values
with `await self.load_settings()`. Nothing is pushed in or preloaded — code pulls
its settings when it needs them, so `MyService()` by hand and `get(...)` through
the registry behave identically.

Lifecycle is a single boolean, `singleton`, enforced by `ServiceMeta` on the
*class*: a singleton's instance is cached on the class, so a hand import
(`MyService()`) and a registry `get(...)` resolve to the same object. The default
is `singleton = False` (build fresh); opt in to `True` only when the service holds
a resource worth reusing (a model client, a db connection).

`close()`/`refresh()` are the only lifecycle hooks. A singleton that opens a
resource lazily on first use overrides `close()` to release it; `refresh()`
(called by the settings endpoint after a save, and at shutdown) closes the live
instance and drops it so the next use rebuilds it with fresh settings. There is no
`setup()` — async wiring happens lazily on first use, not in a build hook.
"""

from abc import ABCMeta
from typing import TYPE_CHECKING

from pydantic import BaseModel, ValidationError

from cat.ambient.runtime import ccat

if TYPE_CHECKING:
    from cat.mad_hatter.plugin import Plugin


class ServiceMeta(ABCMeta):
    """Make `singleton = True` a property of the class.

    Calling a singleton service (`MyService()`) returns one cached instance per
    class, so a manual import and a registry `get(...)` resolve to the *same*
    object. Non-singletons build fresh every call. Subclasses `ABCMeta`, so
    `@abstractmethod` (e.g. on `ModelProvider`, `Auth`) still works.
    """

    def __call__(cls, *args, **kwargs):
        if not cls.singleton:
            return super().__call__(*args, **kwargs)
        # `cls.__dict__` (not getattr) so each subclass caches its OWN instance
        # instead of inheriting a parent singleton's.
        if cls.__dict__.get("_instance") is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class Service(metaclass=ServiceMeta):
    """Base class for framework and plugin services."""

    service_type: str = "base"
    singleton: bool = False

    slug: str | None = None
    name: str | None = None
    description: str | None = None
    plugin_id: str | None = None

    @property
    def plugin(self) -> "Plugin | None":
        """The Plugin that provided this service, if any."""
        if self.plugin_id is None:
            return None
        return ccat().mad_hatter.plugins[self.plugin_id]

    async def close(self) -> None:
        """Release a resource this singleton holds — e.g. `await self.db.close()`.

        Intended for `singleton = True` services that open something on first use
        (a db connection, a client). Called by `refresh()` and at shutdown. Plain
        or non-singleton services that build nothing persistent can ignore it.
        """
        pass

    @classmethod
    async def refresh(cls) -> None:
        """Close the live singleton and drop it; the next use rebuilds it.

        The settings endpoint calls this after saving, so a singleton that cached
        a client/connection picks up the new settings on next resolution. A no-op
        for non-singletons and for singletons that were never instantiated.
        """
        instance = cls.__dict__.get("_instance")
        if instance is not None:
            await instance.close()
            cls._instance = None

    # -- settings ----------------------------------------------------------
    #
    # Three classmethods, so they work the same on the class (the settings
    # routes iterate registered classes) and on an instance (`self.load_settings()`
    # from inside service code). No `app`/`ccat` argument is threaded — the few
    # dynamic schemas that need the registry reach it via ambient `ccat()`.

    @classmethod
    def _settings_key(cls) -> str:
        """Stable DB key for this service's settings blob."""
        return f"settings_{cls.plugin_id}_{cls.service_type}_{cls.slug}"

    @classmethod
    async def value_schema(cls) -> "type[BaseModel] | None":
        """
        The static shape persisted settings are stored and validated against:
        the nested `class Settings(BaseModel)` if declared, else None.

        Cheap and side-effect-free, so it is safe on the hot path —
        `load_settings()` / `save_settings()` resolve it on every read and write.
        `settings_schema()` may *present* these same fields more richly (e.g.
        dropdowns), but values always round-trip through this plain shape.
        """
        nested = getattr(cls, "Settings", None)
        if isinstance(nested, type) and issubclass(nested, BaseModel):
            return nested

        # A dynamic settings_schema() with no static Settings has nothing to
        # validate or persist against — fail loudly instead of silently dropping
        # the values. settings_schema() is presentation; Settings is storage.
        if cls.settings_schema.__func__ is not Service.settings_schema.__func__:
            raise TypeError(
                f"{cls.__name__} overrides settings_schema() but declares no nested "
                "`class Settings(BaseModel)`. settings_schema() is presentation only; "
                "declare a static `Settings` as the stored shape (or override "
                "value_schema())."
            )
        return None

    @classmethod
    async def settings_schema(cls) -> "type[BaseModel] | None":
        """
        The schema the settings UI renders. Defaults to `value_schema()`.

        Override to build a dynamic/enriched presentation (e.g. an enum derived
        from installed plugins). ONLY the settings route calls this — reads and
        writes go through `value_schema()`, so an expensive override never lands
        on the hot path. A dynamic override MUST be backed by a static `Settings`
        (the stored shape); otherwise `value_schema()` raises.
        """
        return await cls.value_schema()

    @classmethod
    async def load_settings(cls) -> "BaseModel | None":
        """
        Current persisted settings as a typed instance, or None if the service
        declares no settings. Read fresh every call — there is no cache and no
        preload, so the value is always current. Loading never destroys the
        stored record: a missing/corrupted blob falls back to defaults, and a
        blob that no longer fully validates is salvaged field-by-field.
        """
        from cat.db import store

        model = await cls.value_schema()
        if model is None:
            return None

        raw = await store.load(cls._settings_key())
        if not isinstance(raw, dict):
            return cls._settings_defaults(model)

        try:
            return model.model_validate(raw)
        except ValidationError:
            return cls._settings_salvage(model, raw)

    @classmethod
    async def save_settings(cls, payload: "dict | BaseModel") -> BaseModel:
        """Validate against the value schema, persist, and return the model."""
        from cat.db import store

        model = await cls.value_schema()
        if model is None:
            raise ValueError(f"{cls.__name__} declares no settings to save.")
        validated = (
            payload if isinstance(payload, BaseModel) else model.model_validate(payload)
        )
        await store.save(cls._settings_key(), validated.model_dump(mode="json"))
        return validated

    # -- settings internals -------------------------------------------------

    @staticmethod
    def _settings_defaults(model: "type[BaseModel]") -> BaseModel:
        """Best-effort defaults instance (settings fields should carry defaults)."""
        try:
            return model()
        except ValidationError:
            # Required-without-default fields: construct without validation so we
            # never crash on load. Convention is to always give defaults.
            return model.model_construct()

    @classmethod
    def _settings_salvage(cls, model: "type[BaseModel]", raw: dict) -> BaseModel:
        """
        Keep every stored value that individually validates against the current
        schema, default the rest. Fall back to full defaults only as a last
        resort. The stored record is never deleted.
        """
        from cat.log import log

        base = cls._settings_defaults(model)
        salvaged = base.model_dump(mode="json")

        for field_name in model.model_fields:
            if field_name not in raw:
                continue
            candidate = dict(salvaged)
            candidate[field_name] = raw[field_name]
            try:
                model.model_validate(candidate)
            except ValidationError:
                continue  # poisoned field → keep its default
            salvaged[field_name] = raw[field_name]

        try:
            return model.model_validate(salvaged)
        except ValidationError as e:
            log.error(f"Could not salvage settings, using defaults: {e}")
            return cls._settings_defaults(model)
