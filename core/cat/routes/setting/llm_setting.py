from typing import Dict

from cat.factory.llm import LLM_SCHEMAS
from cat.db import crud, models
from fastapi import Request, APIRouter, Body, HTTPException

router = APIRouter()

# general LLM settings are saved in settigns table under this category
LLM_SELECTED_CATEGORY = "llm"

# llm type and config are saved in settings table under this category
LLM_CATEGORY = "llm_factory"

# llm selected configuration is saved under this name
LLM_SELECTED_NAME = "llm_selected"


# get configured LLMs and configuration schemas
@router.get("/")
def get_llm_settings():
    """Get the list of the Large Language Models"""

    settings = crud.get_settings_by_category(category=LLM_CATEGORY)
    selected = crud.get_setting_by_name(name=LLM_SELECTED_NAME)

    if selected is None:
        selected_configuration = None
    else:
        selected_configuration = selected["value"]["name"]

    allowed_configurations = list(LLM_SCHEMAS.keys())

    return {
        "status": "success",
        "results": len(settings),
        "settings": settings,
        "schemas": LLM_SCHEMAS,
        "allowed_configurations": allowed_configurations,
        "selected_configuration": selected_configuration,
    }


@router.put("/{languageModelName}")
def upsert_llm_setting(
    request: Request,
    languageModelName: str,
    payload: Dict = Body(example={"openai_api_key": "your-key-here"}),
):
    """Upsert the Large Language Model setting"""

    # check that languageModelName is a valid name
    allowed_configurations = list(LLM_SCHEMAS.keys())
    if languageModelName not in allowed_configurations:
        raise HTTPException(
            status_code=400,
            detail=f"{languageModelName} not supported. Must be one of {allowed_configurations}",
        )
    
    # create the setting and upsert it
    final_setting = crud.upsert_setting_by_name(
        models.Setting(name=languageModelName, category=LLM_CATEGORY, value=payload)
    )

    crud.upsert_setting_by_name(
        models.Setting(name=LLM_SELECTED_NAME, category=LLM_SELECTED_CATEGORY, value={"name":languageModelName})
    )

    status = {
        "status": "success", 
        "setting": final_setting
    }

    # reload the cat at runtime
    ccat = request.app.state.ccat
    ccat.bootstrap()

    return status
