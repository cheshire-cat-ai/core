from typing import Dict, List
from pydantic import BaseModel, Field, ValidationError
from fastapi import APIRouter, HTTPException, Body

from cat.auth.depends import _get_user
from cat.ambient.runtime import ccat

router = APIRouter(prefix="/settings", tags=["Settings"])


class SettingsEntry(BaseModel):
    """A single service's settings entry."""
    id: str
    slug: str
    type: str
    name: str
    plugin_id: str | None
    value: dict
    schema_: dict | None = Field(None, alias="schema")

    model_config = {"populate_by_name": True}


def _make_id(plugin_id: str | None, service_type: str, slug: str) -> str:
    return f"{plugin_id}__{service_type}__{slug}"


def _parse_id(id: str) -> tuple[str, str, str]:
    parts = id.split("__")
    if len(parts) != 3:
        raise HTTPException(status_code=404, detail=f"Invalid settings id: {id}")
    return parts[0], parts[1], parts[2]


@router.get("")
async def list_settings(
    user=_get_user(role="admin"),
) -> List[SettingsEntry]:
    """
    List all services that have settings, with metadata, current values, and
    schemas. One resolution path — `settings_schema()` — for both static and
    dynamic schemas.
    """
    entries = []

    for service_type, service_dict in ccat().registry.classes.items():
        for slug, ServiceClass in service_dict.items():

            model = await ServiceClass.settings_schema()
            if model is None:
                continue

            current = await ServiceClass.load_settings()

            entries.append(SettingsEntry(
                id=_make_id(ServiceClass.plugin_id, service_type, slug),
                slug=slug,
                type=service_type,
                name=ServiceClass.name or ServiceClass.__name__,
                plugin_id=ServiceClass.plugin_id,
                value=current.model_dump(mode="json"),
                schema=model.model_json_schema(),
            ))

    return entries


@router.put("/{id}")
async def update_settings(
    id: str,
    payload: Dict = Body(...),
    user=_get_user(role="admin"),
) -> SettingsEntry:
    """
    Save settings for a single service identified by its composite id.
    Validates against the current schema via `ServiceClass.save_settings`, then
    refreshes the affected service (drop the cached singleton) so the next
    resolution rebuilds it and re-reads the new settings.
    """
    plugin_id, service_type, slug = _parse_id(id)

    ServiceClass = ccat().registry.classes.get(service_type, {}).get(slug)
    if ServiceClass is None or ServiceClass.plugin_id != plugin_id:
        raise HTTPException(status_code=404, detail=f"Settings {id} not found")

    model = await ServiceClass.settings_schema()
    if model is None:
        raise HTTPException(
            status_code=400,
            detail=f"Settings {id} does not support settings",
        )

    try:
        saved = await ServiceClass.save_settings(payload)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.errors())

    # Targeted refresh — only restart the affected service.
    await ccat().registry.refresh(service_type, slug)

    return SettingsEntry(
        id=id,
        slug=slug,
        type=service_type,
        name=ServiceClass.name or ServiceClass.__name__,
        plugin_id=ServiceClass.plugin_id,
        value=saved.model_dump(mode="json"),
        schema=model.model_json_schema(),
    )
