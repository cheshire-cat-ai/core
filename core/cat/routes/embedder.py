from typing import Dict

from fastapi import Request, APIRouter, Body, HTTPException

from cat.factory.embedder import EMBEDDER_SCHEMAS, SUPPORTED_EMDEDDING_MODELS
from cat.db import crud, models
from cat.log import log

router = APIRouter()

# general embedder settings are saved in settings table under this category
EMBEDDER_SELECTED_CATEGORY = "embedder"

# embedder type and config are saved in settings table under this category
EMBEDDER_CATEGORY = "embedder_factory"

# embedder selected configuration is saved under this name
EMBEDDER_SELECTED_NAME = "embedder_selected"


# get configured Embedders and configuration schemas
@router.get("/settings/")
def get_embedders_settings(request: Request) -> Dict:
    """Get the list of the Embedders"""

    # get selected Embedder, if any
    selected = crud.get_setting_by_name(name=EMBEDDER_SELECTED_NAME)
    if selected is not None:
        selected = selected["value"]["name"]
    # If DB does not contain a selected embedder, it means an embedder was automatically selected.
    # Deduce selected embedder:
    ccat = request.app.state.ccat
    for embedder_config_class in reversed(SUPPORTED_EMDEDDING_MODELS):
        if embedder_config_class._pyclass.default == type(ccat.embedder):
            selected = embedder_config_class.__name__
    
    saved_settings = crud.get_settings_by_category(category=EMBEDDER_CATEGORY)
    saved_settings = { s["name"]: s for s in saved_settings }

    settings = []
    for class_name, schema in EMBEDDER_SCHEMAS.items():
        
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


# get Embedder settings and its schema
@router.get("/settings/{languageEmbedderName}")
def get_embedder_settings(request: Request, languageEmbedderName: str) -> Dict:
    """Get settings and schema of the specified Embedder"""

    # check that languageEmbedderName is a valid name
    allowed_configurations = list(EMBEDDER_SCHEMAS.keys())
    if languageEmbedderName not in allowed_configurations:
        raise HTTPException(
            status_code=400,
            detail={
                "error": f"{languageEmbedderName} not supported. Must be one of {allowed_configurations}"
            }
        )
    
    setting = crud.get_setting_by_name(name=languageEmbedderName)
    schema = EMBEDDER_SCHEMAS[languageEmbedderName]

    if setting is None:
        setting = {}
    else:
        setting = setting["value"]

    return {
        "name": languageEmbedderName,
        "value": setting,
        "schema": schema
    }


@router.put("/settings/{languageEmbedderName}")
def upsert_embedder_setting(
    request: Request,
    languageEmbedderName: str,
    payload: Dict = Body(example={"openai_api_key": "your-key-here"}),
) -> Dict:
    """Upsert the Embedder setting"""
    
    # check that languageModelName is a valid name
    allowed_configurations = list(EMBEDDER_SCHEMAS.keys())
    if languageEmbedderName not in allowed_configurations:
        raise HTTPException(
            status_code=400,
            detail={
                "error": f"{languageEmbedderName} not supported. Must be one of {allowed_configurations}"
            }
        )
    
    # create the setting and upsert it
    final_setting = crud.upsert_setting_by_name(
        models.Setting(name=languageEmbedderName, category=EMBEDDER_CATEGORY, value=payload)
    )

    crud.upsert_setting_by_name(
        models.Setting(name=EMBEDDER_SELECTED_NAME, category=EMBEDDER_SELECTED_CATEGORY, value={"name":languageEmbedderName})
    )

    status = {
        "name": languageEmbedderName,
        "value": final_setting["value"]
    }

    ccat = request.app.state.ccat
    # reload llm and embedder of the cat
    ccat.load_natural_language()
    # crete new collections (different embedder!)
    ccat.load_memory()
    # recreate tools embeddings
    ccat.mad_hatter.find_plugins()
    ccat.mad_hatter.embed_tools()

    return status
