from typing import Dict

from fastapi import Depends, Request, APIRouter
from sqlalchemy.orm import Session
from cat.db.database import get_db_session
from cat.routes.setting import setting_utils
from cat.factory.embedder import EMBEDDER_SCHEMAS

router = APIRouter()

# general LLM settings are saved in settigns table under this category
EMBEDDER_DB_GENERAL_CATEGORY = "embedder"

# llm type and config are saved in settings table under this category
EMBEDDER_DB_FACTORY_CATEGORY = "embedder_factory"

# llm selected configuration is saved under this name
EMBEDDER_SELECTED_CONFIGURATION = "embedder_selected"


# get configured LLMs and configuration schemas
@router.get("/")
def get_settings(db: Session = Depends(get_db_session)):
    return setting_utils.nlp_get_settings(
        db,
        setting_factory_category=EMBEDDER_DB_FACTORY_CATEGORY,
        setting_selected_name=EMBEDDER_SELECTED_CONFIGURATION,
        schemas=EMBEDDER_SCHEMAS,
    )


@router.put("/{languageEmbedderName}")
def upsert_llm_setting(
    request: Request,
    languageEmbedderName: str,
    payload: Dict = setting_utils.nlp_get_example_put_payload(),
    db: Session = Depends(get_db_session),
):
    db_naming = {
        "setting_factory_category": EMBEDDER_DB_FACTORY_CATEGORY,
        "setting_selected_category": EMBEDDER_DB_GENERAL_CATEGORY,
        "setting_selected_name": EMBEDDER_SELECTED_CONFIGURATION,
    }

    # update settings DB
    status = setting_utils.put_nlp_setting(
        db,
        modelName=languageEmbedderName,
        payload=payload,
        db_naming=db_naming,
        schemas=EMBEDDER_SCHEMAS,
    )

    # reload the cat at runtime
    # TODO: delete old embedding space
    # ccat = request.app.state.ccat
    # ccat.bootstrap()

    return status
