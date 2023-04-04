from typing import Dict

from cat.db import crud, models
from fastapi import Body, Depends, APIRouter, HTTPException
from cat.config.llm import LLM_SCHEMAS
from sqlalchemy.orm import Session
from cat.db.database import get_db_session

router = APIRouter()

# llm type and config are saved in settings table under this category
LLM_DB_CATEGORY = "llm_factory"

# list of configurable models
ALLOWED_LLM_CONGURATIONS = list(LLM_SCHEMAS.keys())


# get configured LLMs and configuration schemas
@router.get("/")
def get_llm_settings(db: Session = Depends(get_db_session)):
    llm_settings = crud.get_settings_by_category(db, category=LLM_DB_CATEGORY)

    return {
        "status": "success",
        "results": len(llm_settings),
        "settings": llm_settings,
        "schemas": LLM_SCHEMAS,
        "allowed_llm_configurations": ALLOWED_LLM_CONGURATIONS,
    }


# example payload to PUT the language model config (will be shown in Swagger UI)
example_put_request = {"openai_api_key": "your-key-here"}

ExamplePutBody = Body(example=example_put_request)


@router.put("/{languageModelName}")
def upsert_llm_setting(
    languageModelName: str,
    payload: Dict = ExamplePutBody,
    db: Session = Depends(get_db_session),
):
    if languageModelName not in ALLOWED_LLM_CONGURATIONS:
        raise HTTPException(
            status_code=400,
            detail=f"{languageModelName} not supported. Must be one of {ALLOWED_LLM_CONGURATIONS}",
        )

    # is the setting already present in DB?
    old_setting = crud.get_setting_by_name(db, languageModelName)

    if old_setting is None:
        # prepare setting to be included in DB, adding category
        llm_setting = {
            "name": languageModelName,
            "value": payload,
            "category": LLM_DB_CATEGORY,
        }
        llm_setting = models.Setting(**llm_setting)
        final_llm_setting = crud.create_setting(db, llm_setting)

    else:
        old_setting.value = payload
        db.add(old_setting)
        db.commit()
        db.refresh(old_setting)
        final_llm_setting = old_setting

    return {"status": "success", "setting": final_llm_setting}
