from typing import Dict

from cat.db import crud
from fastapi import Body, HTTPException
from sqlalchemy.orm import Session


# utility function to GET LLMs and embedders configuration (used from both /settings/llm/ and /settings/embedder/ endpoints)
def nlp_get_settings(
    db: Session,
    setting_factory_category: str,
    setting_selected_name: str,
    schemas: Dict,
):
    # list of configurable models
    allowed_configurations = list(schemas.keys())

    # retrieve all saved configurations (including currently selected one)
    settings = crud.get_settings_by_category(db, category=setting_factory_category)

    # retrieve current selected model (has to be one)
    selected = crud.get_setting_by_name(db, name=setting_selected_name)
    if selected is None:
        selected_configuration = None
    else:
        selected_configuration = selected.value["name"]

    return {
        "status": "success",
        "results": len(settings),
        "settings": settings,
        "schemas": schemas,
        "allowed_configurations": allowed_configurations,
        "selected_configuration": selected_configuration,
    }


# example payload to PUT the language model / embedder config (will be shown in Swagger UI)
def nlp_get_example_put_payload():
    example_put_request = {"openai_api_key": "your-key-here"}
    ExamplePutBody = Body(example=example_put_request)
    return ExamplePutBody


# utility function to PUT LLMs and embedders configuration (used from both /settings/llm/ and /settings/embedder/ endpoints)
def put_nlp_setting(
    db: Session,
    modelName: str,
    payload: Dict,
    db_naming: Dict,
    schemas: Dict,
):
    # list of configurable models
    allowed_configurations = list(schemas.keys())
    if modelName not in allowed_configurations:
        raise HTTPException(
            status_code=400,
            detail=f"{modelName} not supported. Must be one of {allowed_configurations}",
        )
    
    final_setting =  crud.upsert_setting(db, name=modelName, category=db_naming["setting_factory_category"], payload=payload)

    # update selected model in DB
    crud.upsert_setting(db, name=db_naming["setting_selected_name"], category=db_naming["setting_selected_category"], payload={"name":modelName})

    return {
        "status": "success", 
        "setting": final_setting
    }
