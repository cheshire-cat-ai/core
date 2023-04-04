from typing import Dict

from cat.db import crud, models
from fastapi import Body, Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from cat.db.database import get_db_session
from cat.config.embedder import EMBEDDER_SCHEMAS

router = APIRouter()

# embedder type and config are saved in settings table under this category
EMBEDDER_DB_CATEGORY = "embedder_factory"

# list of configurable embedders
ALLOWED_EMBEDDER_CONGURATIONS = list(EMBEDDER_SCHEMAS.keys())


# get configured embedders and configuration schemas
@router.get("/")
def get_llm_settings(db: Session = Depends(get_db_session)):
    embedder_settings = crud.get_settings_by_category(db, category=EMBEDDER_DB_CATEGORY)

    return {
        "status": "success",
        "results": len(embedder_settings),
        "settings": embedder_settings,
        "schemas": EMBEDDER_SCHEMAS,
        "allowed_llm_configurations": ALLOWED_EMBEDDER_CONGURATIONS,
    }


# example payload to PUT the embedder config (will be shown in Swagger UI)
example_put_request = {"openai_api_key": "your-key-here"}

ExamplePutBody = Body(example=example_put_request)


@router.put("/{languageEmbedderName}")
def upsert_llm_setting(
    languageEmbedderName: str,
    payload: Dict = ExamplePutBody,
    db: Session = Depends(get_db_session),
):
    if languageEmbedderName not in ALLOWED_EMBEDDER_CONGURATIONS:
        raise HTTPException(
            status_code=400,
            detail=f"{languageEmbedderName} not supported. Must be one of {ALLOWED_EMBEDDER_CONGURATIONS}",
        )

    # is the setting already present in DB?
    old_setting = crud.get_setting_by_name(db, languageEmbedderName)

    if old_setting is None:
        # prepare setting to be included in DB, adding category
        embedder_setting = {
            "name": languageEmbedderName,
            "value": payload,
            "category": EMBEDDER_DB_CATEGORY,
        }
        embedder_setting = models.Setting(**embedder_setting)
        final_embedder_setting = crud.create_setting(db, embedder_setting)

    else:
        old_setting.value = payload
        db.add(old_setting)
        db.commit()
        db.refresh(old_setting)
        final_embedder_setting = old_setting

    return {"status": "success", "setting": final_embedder_setting}
