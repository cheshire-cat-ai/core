"""
Stateless settings manager.

Settings persistence used to live on `Service` (`load_settings`/`save_settings`).
It now lives here, off the service, so a `Service` is just a noun with a typed
`self.settings` the registry injects before `setup()`.

The manager holds no cache: `self.settings` on a live service is the only
per-lifecycle cache. It is keyed by a stable per-service key and is robust by
construction — loading never destroys saved data. A corrupted blob falls back
to defaults; a blob that no longer validates is salvaged field-by-field (keep
every value that still validates, default the rest) and is never deleted.
"""

from typing import TYPE_CHECKING

from pydantic import BaseModel, ValidationError

from cat.db import DB
from cat import log

if TYPE_CHECKING:
    from cat.services.service import Service
    from cat.looking_glass.cheshire_cat import CheshireCat


class SettingsManager:
    """Loads and saves service settings. Stateless and shared."""

    @staticmethod
    def key(ServiceClass: "type[Service]") -> str:
        """Stable DB key for a service's settings."""
        return f"settings_{ServiceClass.plugin_id}_{ServiceClass.service_type}_{ServiceClass.slug}"

    async def load(
        self, ServiceClass: "type[Service]", app: "CheshireCat"
    ) -> BaseModel | None:
        """
        Return the typed settings instance for a service, or None if it has no
        settings. Reads the stored blob and reconciles it with the current
        schema without ever deleting the stored record.
        """
        model = await ServiceClass.settings_schema(app)
        if model is None:
            return None

        raw = await DB.load(self.key(ServiceClass))

        # Missing or corrupted (non-dict) blob → class defaults.
        if not isinstance(raw, dict):
            return self._defaults(model)

        try:
            return model.model_validate(raw)
        except ValidationError:
            # Schema changed or a field is poisoned → salvage field-by-field.
            return self._salvage(model, raw)

    async def save(
        self, ServiceClass: "type[Service]", app: "CheshireCat", payload: dict | BaseModel
    ) -> BaseModel:
        """Validate against the current schema, persist, and return the model."""
        model = await ServiceClass.settings_schema(app)
        if model is None:
            raise ValueError(
                f"{ServiceClass.__name__} declares no settings to save."
            )
        validated = (
            payload if isinstance(payload, BaseModel) else model.model_validate(payload)
        )
        await DB.save(self.key(ServiceClass), validated.model_dump(mode="json"))
        return validated

    # -- internals ----------------------------------------------------------

    @staticmethod
    def _defaults(model: type[BaseModel]) -> BaseModel:
        """Best-effort defaults instance (settings fields should carry defaults)."""
        try:
            return model()
        except ValidationError:
            # Required-without-default fields: construct without validation so
            # we never crash on load. Convention is to always give defaults.
            return model.model_construct()

    def _salvage(self, model: type[BaseModel], raw: dict) -> BaseModel:
        """
        Keep every stored value that individually validates against the current
        schema, default the rest. Only fall back to full defaults as a last
        resort. The stored record is never deleted.
        """
        base = self._defaults(model)
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
            return self._defaults(model)


# One shared, stateless manager.
settings = SettingsManager()
