from typing import Dict, List
from inspect import isclass
from pydantic import BaseModel, Field, ValidationError
from fastapi import APIRouter, Request, HTTPException, Body

from cat.auth import get_user, get_ccat
from cat.db import DB
from cat import log

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


def _has_settings_model_override(ServiceClass) -> bool:
    """Check if a service class overrides settings_model() beyond the base default."""
    return "settings_model" in ServiceClass.__dict__


def _get_nested_settings(ServiceClass) -> type | None:
    """Get the nested Settings class from a service class, if it exists."""
    nested = getattr(ServiceClass, 'Settings', None)
    if nested is not None and isclass(nested) and issubclass(nested, BaseModel):
        return nested
    return None


@router.get("")
async def list_settings(
    r: Request,
    user=get_user(role="admin"),
    ccat=get_ccat(),
) -> List[SettingsEntry]:
    """
    List all services that have settings, with metadata, current values, and schemas.
    """

    entries = []
    for service_type, service_dict in ccat.factory.class_index.items():
        for slug, ServiceClass in service_dict.items():
            db_key = ServiceClass._settings_db_key()

            # Try static nested Settings class first (no instantiation needed)
            nested = _get_nested_settings(ServiceClass)

            if nested is not None and not _has_settings_model_override(ServiceClass):
                # Static schema — no instance needed
                settings_schema = nested.model_json_schema()
                raw = await DB.load(db_key)
                value = raw if raw is not None else nested().model_dump()
            elif _has_settings_model_override(ServiceClass):
                # Dynamic schema — need running instance
                try:
                    if ServiceClass.lifecycle == "request":
                        instance = await ccat.get(service_type, slug, request=r)
                    else:
                        instance = await ccat.get(service_type, slug)
                except Exception as e:
                    log.error(f"Error getting service {service_type}:{slug} for settings: {e}")
                    continue

                model = await instance.settings_model()
                if model is None:
                    continue
                settings_schema = model.model_json_schema()
                raw = await DB.load(db_key)
                value = raw if raw is not None else model().model_dump()
            else:
                # No settings at all
                continue

            entries.append(SettingsEntry(
                id=_make_id(ServiceClass.plugin_id, service_type, slug),
                slug=slug,
                type=service_type,
                name=ServiceClass.name or ServiceClass.__name__,
                plugin_id=ServiceClass.plugin_id,
                value=value,
                schema=settings_schema,
            ))

    return entries


@router.put("/{id}")
async def update_settings(
    id: str,
    r: Request,
    payload: Dict = Body(...),
    user=get_user(role="admin"),
    ccat=get_ccat(),
) -> SettingsEntry:
    """
    Save settings for a single service identified by its composite id.
    Validates against schema, saves to DB, refreshes the affected service.
    """
    plugin_id, service_type, slug = _parse_id(id)

    # Look up the service class
    ServiceClass = ccat.factory.class_index.get(service_type, {}).get(slug)
    if ServiceClass is None or ServiceClass.plugin_id != plugin_id:
        raise HTTPException(
            status_code=404,
            detail=f"Settings {id} not found"
        )

    # Resolve settings model
    nested = _get_nested_settings(ServiceClass)
    if _has_settings_model_override(ServiceClass):
        # Need instance for dynamic schema
        try:
            if ServiceClass.lifecycle == "request":
                instance = await ccat.get(service_type, slug, request=r)
            else:
                instance = await ccat.get(service_type, slug)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        settings_model = await instance.settings_model()
    elif nested is not None:
        settings_model = nested
    else:
        settings_model = None

    if settings_model is None:
        raise HTTPException(
            status_code=400,
            detail=f"Settings {id} does not support settings"
        )

    # Validate
    try:
        validated = settings_model.model_validate(payload)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.errors())

    # Save to DB
    db_key = ServiceClass._settings_db_key()
    saved = validated.model_dump()
    await DB.save(db_key, saved)

    # Targeted refresh — only restart the affected service
    await ccat.factory.refresh(service_type, slug)

    return SettingsEntry(
        id=id,
        slug=slug,
        type=service_type,
        name=ServiceClass.name or ServiceClass.__name__,
        plugin_id=ServiceClass.plugin_id,
        value=saved,
        schema=settings_model.model_json_schema(),
    )
