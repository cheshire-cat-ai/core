from typing import Dict
from fastapi import Request, APIRouter, Body, HTTPException

from cat.looking_glass.stray_cat import StrayCat
from cat.db import crud, models
from cat.factory.auth_handler import get_auth_handlers_schemas
from cat.auth.permissions import AuthPermission, AuthResource, check_permissions

router = APIRouter()

AUTH_HANDLER_SELECTED_NAME = "auth_handler_selected"

AUTH_HANDLER_CATEGORY = "auth_handler_factory"


@router.get("/settings")
def get_auth_handler_settings(
    request: Request,
    cat: StrayCat = check_permissions(AuthResource.AUTH_HANDLER, AuthPermission.LIST),
) -> Dict:
    """Get the list of the AuthHandlers"""

    # get selected AuthHandler
    selected = crud.get_setting_by_name(name=AUTH_HANDLER_SELECTED_NAME)
    if selected is not None:
        selected = selected["value"]["name"]

    saved_settings = crud.get_settings_by_category(category=AUTH_HANDLER_CATEGORY)
    saved_settings = {s["name"]: s for s in saved_settings}

    settings = []
    for class_name, schema in get_auth_handlers_schemas().items():
        if class_name in saved_settings:
            saved_setting = saved_settings[class_name]["value"]
        else:
            saved_setting = {}

        settings.append(
            {
                "name": class_name,
                "value": saved_setting,
                "schema": schema,
            }
        )

    return {
        "settings": settings,
        "selected_configuration": selected,
    }


@router.get("/settings/{auth_handler_name}")
def get_auth_handler_setting(
    request: Request,
    auth_handler_name: str,
    cat: StrayCat = check_permissions(AuthResource.AUTH_HANDLER, AuthPermission.READ),
) -> Dict:
    """Get the settings of a specific AuthHandler"""

    AUTH_HANDLER_SCHEMAS = get_auth_handlers_schemas()

    allowed_configurations = list(AUTH_HANDLER_SCHEMAS.keys())
    if auth_handler_name not in allowed_configurations:
        raise HTTPException(
            status_code=400,
            detail={
                "error": f"{auth_handler_name} not supported. Must be one of {allowed_configurations}"
            },
        )

    setting = crud.get_setting_by_name(name=auth_handler_name)
    schema = AUTH_HANDLER_SCHEMAS[auth_handler_name]

    if setting is None:
        setting = {}
    else:
        setting = setting["value"]

    return {"name": auth_handler_name, "value": setting, "schema": schema}


@router.put("/settings/{auth_handler_name}")
def upsert_authenticator_setting(
    request: Request,
    auth_handler_name: str,
    payload: Dict = Body(...),
    cat: StrayCat = check_permissions(AuthResource.AUTH_HANDLER, AuthPermission.EDIT),
) -> Dict:
    """Upsert the settings of a specific AuthHandler"""

    AUTH_HANDLER_SCHEMAS = get_auth_handlers_schemas()

    allowed_configurations = list(AUTH_HANDLER_SCHEMAS.keys())
    if auth_handler_name not in allowed_configurations:
        raise HTTPException(
            status_code=400,
            detail={
                "error": f"{auth_handler_name} not supported. Must be one of {allowed_configurations}"
            },
        )

    crud.upsert_setting_by_name(
        models.Setting(
            name=auth_handler_name, value=payload, category=AUTH_HANDLER_CATEGORY
        )
    )

    crud.upsert_setting_by_name(
        models.Setting(
            name=AUTH_HANDLER_SELECTED_NAME,
            value={"name": auth_handler_name},
            category=AUTH_HANDLER_CATEGORY,
        )
    )

    request.app.state.ccat.load_auth()

    return {
        "name": auth_handler_name,
        "value": payload,
    }
