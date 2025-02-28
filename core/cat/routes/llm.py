from typing import Dict

from cat.auth.permissions import AuthPermission, AuthResource, check_permissions
from fastapi import Request, APIRouter, Body, HTTPException

from cat.factory.llm import get_llms_schemas
from cat.db import crud, models
from cat.log import log
from cat import utils

router = APIRouter()

# general LLM settings are saved in settigns table under this category
LLM_SELECTED_CATEGORY = "llm"

# llm type and config are saved in settings table under this category
LLM_CATEGORY = "llm_factory"

# llm selected configuration is saved under this name
LLM_SELECTED_NAME = "llm_selected"


# get configured LLMs and configuration schemas
@router.get("/settings")
def get_llms_settings(
    cat=check_permissions(AuthResource.LLM, AuthPermission.LIST),
) -> Dict:
    """Get the list of the Large Language Models"""
    LLM_SCHEMAS = get_llms_schemas()

    # get selected LLM, if any
    selected = crud.get_setting_by_name(name=LLM_SELECTED_NAME)
    if selected is not None:
        selected = selected["value"]["name"]

    saved_settings = crud.get_settings_by_category(category=LLM_CATEGORY)
    saved_settings = {s["name"]: s for s in saved_settings}

    settings = []
    for class_name, schema in LLM_SCHEMAS.items():
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


# get LLM settings and its schema
@router.get("/settings/{languageModelName}")
def get_llm_settings(
    request: Request,
    languageModelName: str,
    cat=check_permissions(AuthResource.LLM, AuthPermission.READ),
) -> Dict:
    """Get settings and schema of the specified Large Language Model"""
    LLM_SCHEMAS = get_llms_schemas()

    # check that languageModelName is a valid name
    allowed_configurations = list(LLM_SCHEMAS.keys())
    if languageModelName not in allowed_configurations:
        raise HTTPException(
            status_code=400,
            detail={
                "error": f"{languageModelName} not supported. Must be one of {allowed_configurations}"
            },
        )

    setting = crud.get_setting_by_name(name=languageModelName)
    schema = LLM_SCHEMAS[languageModelName]

    if setting is None:
        setting = {}
    else:
        setting = setting["value"]

    return {"name": languageModelName, "value": setting, "schema": schema}


@router.put("/settings/{languageModelName}")
def upsert_llm_setting(
    request: Request,
    languageModelName: str,
    payload: Dict = Body({"openai_api_key": "your-key-here"}),
    cat=check_permissions(AuthResource.LLM, AuthPermission.EDIT),
) -> Dict:
    """Upsert the Large Language Model setting"""
    LLM_SCHEMAS = get_llms_schemas()

    # check that languageModelName is a valid name
    allowed_configurations = list(LLM_SCHEMAS.keys())
    if languageModelName not in allowed_configurations:
        raise HTTPException(
            status_code=400,
            detail={
                "error": f"{languageModelName} not supported. Must be one of {allowed_configurations}"
            },
        )

    # create the setting and upsert it
    final_setting = crud.upsert_setting_by_name(
        models.Setting(name=languageModelName, category=LLM_CATEGORY, value=payload)
    )

    crud.upsert_setting_by_name(
        models.Setting(
            name=LLM_SELECTED_NAME,
            category=LLM_SELECTED_CATEGORY,
            value={"name": languageModelName},
        )
    )

    status = {"name": languageModelName, "value": final_setting["value"]}

    ccat = request.app.state.ccat
    # reload llm and embedder of the cat
    ccat.load_natural_language()
    # crete new collections
    # (in case embedder is not configured, it will be changed automatically and aligned to vendor)
    # TODO: should we take this feature away?
    # Exception handling in case an incorrect key is loaded.
    try:
        ccat.load_memory()
    except Exception as e:
        log.error("Error while changing LLM")
        crud.delete_settings_by_category(category=LLM_SELECTED_CATEGORY)
        crud.delete_settings_by_category(category=LLM_CATEGORY)
        raise HTTPException(
            status_code=400, detail={"error": utils.explicit_error_message(e)}
        )
    # recreate tools embeddings
    ccat.mad_hatter.find_plugins()

    return status
