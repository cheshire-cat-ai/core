from typing import Dict

from fastapi import Request, APIRouter, Body, HTTPException
from cat.db import crud, models
from cat.db.database import Database
from cat.factory.embedder import EMBEDDER_SCHEMAS

router = APIRouter()

# general embedder settings are saved in settings table under this category
EMBEDDER_SELECTED_CATEGORY = "embedder"

# embedder type and config are saved in settings table under this category
EMBEDDER_CATEGORY = "embedder_factory"

# embedder selected configuration is saved under this name
EMBEDDER_SELECTED_NAME = "embedder_selected"


# get configured Embedders and configuration schemas
@router.get("/")
def get_embedder_settings():
    """Get the list of the Embedders"""
    settings = crud.get_settings_by_category(category=EMBEDDER_CATEGORY)
    selected = crud.get_setting_by_name(name=EMBEDDER_SELECTED_NAME)

    if selected is None:
        selected_configuration = None
    else:
        selected_configuration = selected.name

    allowed_configurations = list(EMBEDDER_SCHEMAS.keys())

    return {
        "status": "success",
        "results": len(settings),
        "settings": settings,
        "schemas": EMBEDDER_SCHEMAS,
        "allowed_configurations": allowed_configurations,
        "selected_configuration": selected_configuration,
    }

@router.put("/{languageEmbedderName}")
def upsert_embedder_setting(
    request: Request,
    languageEmbedderName: str,
    payload: Dict = Body(example={"openai_api_key": "your-key-here"}),
):
    """Upsert the Embedder setting"""
    
    # check that languageModelName is a valid name
    allowed_configurations = list(EMBEDDER_SCHEMAS.keys())
    if languageEmbedderName not in allowed_configurations:
        raise HTTPException(
            status_code=400,
            detail=f"{languageEmbedderName} not supported. Must be one of {allowed_configurations}",
        )
    
    # create the setting and upsert it
    final_setting = crud.upsert_setting_by_name(
        models.Setting(name=languageEmbedderName, category=EMBEDDER_CATEGORY, value=payload)
    )

    crud.upsert_setting_by_name(
        models.Setting(name=EMBEDDER_SELECTED_NAME, category=EMBEDDER_SELECTED_CATEGORY, value={"name":languageEmbedderName})
    )

    status = {
        "status": "success", 
        "setting": final_setting
    }

    # reload the cat at runtime
    ccat = request.app.state.ccat
    ccat.bootstrap()

    return status
