from typing import Dict

from cat.db import crud, models
from cat.factory.authorizator import get_allowed_authorizator_strategies, get_authorizators_schemas
from fastapi import Request, APIRouter, Body, HTTPException

router = APIRouter()

AUTHORIZAOTOR_SELECTED_NAME = "authorizator_selected"

AUTHORIZAOTOR_CATEGORY = "authorizator_factory"

@router.get("/settings")
def get_authorizator_settings(request: Request) -> Dict:
    """Get the list of the Authorizators"""

    SUPPORTED_AUTHORIZATORS = get_allowed_authorizator_strategies()
    
    # get selected Authorizator, if any
    selected = crud.get_setting_by_name(name=AUTHORIZAOTOR_SELECTED_NAME)
    if selected is not None:
        selected = selected["value"]["name"]
    else:
        # If DB does not contain a selected authorizator, it means an authorizator was automatically selected.
        # Deduce selected authorizator:
        ccat = request.app.state.ccat
        for authorizator_config_class in reversed(SUPPORTED_AUTHORIZATORS):
            if authorizator_config_class._pyclass.default == type(ccat.authorizator):
                selected = authorizator_config_class.__name__
    
    saved_settings = crud.get_settings_by_category(category=AUTHORIZAOTOR_CATEGORY)
    saved_settings = { s["name"]: s for s in saved_settings }

    settings = []

    for class_name, schema in get_authorizators_schemas().items():
        
        if class_name in saved_settings:
            saved_setting = saved_settings[class_name]["value"]
        else:
            saved_setting = {}

        settings.append({
            "name"  : class_name,
            "value" : saved_setting,
            "schema": schema,
        })

    return {
        "settings": settings,
        "selected_configuration": selected,
    }

@router.get("/settings/{authorizator_name}")
def get_authorizator_setting(request: Request, authorizator_name: str) -> Dict:
    """Get the settings of a specific Authorizator"""

    AUTHORIZATOR_SCHEMAS = get_authorizators_schemas()

    allowed_configurations  = list(AUTHORIZATOR_SCHEMAS.keys())
    from cat.log import log
    log.error(f"Allowed configurations: {allowed_configurations}")
    if authorizator_name not in allowed_configurations:
        raise HTTPException(
            status_code=400, 
            detail={
                "error": f"{authorizator_name} not supported"
            }
        )
    
    setting = crud.get_setting_by_name(name=authorizator_name)

    schema = AUTHORIZATOR_SCHEMAS[authorizator_name]
    
    return {
        "name"  : authorizator_name,
        "value" : setting["value"] if setting is not None else {},
        "schema": schema,
    }

@router.put("/settings/{authorizator_name}")
def upsert_authenticator_setting(
    request: Request,
    authorizator_name: str,
    payload: Dict = Body(...),
) -> Dict:
    """Upsert the settings of a specific Authorizator"""

    AUTHORIZATOR_SCHEMAS = get_authorizators_schemas()

    allowed_configurations  = list(AUTHORIZATOR_SCHEMAS.keys())
    if authorizator_name not in allowed_configurations:
        raise HTTPException(
            status_code=400,
            detail={
                "error": f"{authorizator_name} not supported"
            }
        )
    
    crud.upsert_setting_by_name(
        models.Setting(
            name=authorizator_name,
            value=payload,
            category=AUTHORIZAOTOR_CATEGORY
        )
    )

    crud.upsert_setting_by_name(
        models.Setting(
            name=AUTHORIZAOTOR_SELECTED_NAME,
            value={"name": authorizator_name},
            category=AUTHORIZAOTOR_CATEGORY
        )
    )

    request.app.state.ccat.load_authorizator()

    return {
        "name"  : authorizator_name,
        "value" : payload,
    }
