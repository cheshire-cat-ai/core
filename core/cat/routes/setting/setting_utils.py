from typing import Dict

from cat.db import crud, models
from fastapi import Body, HTTPException
from sqlalchemy import func
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

    # upsert setting. TODO: move this in db.crud functions as crud.upsert_setting
    # is the setting already present in DB?
    old_setting = crud.get_setting_by_name(db, modelName)

    if old_setting is None:
        # prepare setting to be included in DB, adding category
        setting = {
            "name": modelName,
            "value": payload,
            "category": db_naming["setting_factory_category"],
        }
        setting = models.Setting(**setting)
        final_setting = crud.create_setting(db, setting).dict()

    else:
        old_setting.value = payload
        old_setting.updatedAt = func.now()
        db.add(old_setting)
        db.commit()
        db.refresh(old_setting)
        final_setting = old_setting.dict()

    # update selected model in DB
    crud.delete_setting_by_name(db, db_naming["setting_selected_name"])
    selected_setting = {
        "name": db_naming["setting_selected_name"],
        "value": {"name": modelName},
        "category": db_naming["setting_selected_category"],
    }
    selected_setting = models.Setting(**selected_setting)
    crud.create_setting(db, selected_setting)

    return {"status": "success", "setting": final_setting}
