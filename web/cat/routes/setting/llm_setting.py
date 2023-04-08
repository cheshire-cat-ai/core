from typing import Dict

from fastapi import Depends, APIRouter
from cat.config.llm import LLM_SCHEMAS
from sqlalchemy.orm import Session
from cat.db.database import get_db_session
from cat.routes.setting import setting_utils

router = APIRouter()

# general LLM settings are saved in settigns table under this category
LLM_DB_GENERAL_CATEGORY = "llm"

# llm type and config are saved in settings table under this category
LLM_DB_FACTORY_CATEGORY = "llm_factory"

# llm selected configuration is saved under this name
LLM_SELECTED_CONFIGURATION = "llm_selected"


# get configured LLMs and configuration schemas
@router.get("/")
def get_settings(db: Session = Depends(get_db_session)):
    return setting_utils.nlp_get_settings(
        db,
        setting_factory_category=LLM_DB_FACTORY_CATEGORY,
        setting_selected_name=LLM_SELECTED_CONFIGURATION,
        schemas=LLM_SCHEMAS,
    )


@router.put("/{languageModelName}")
def upsert_llm_setting(
    languageModelName: str,
    payload: Dict = setting_utils.nlp_get_example_put_payload(),
    db: Session = Depends(get_db_session),
):
    db_naming = {
        "setting_factory_category": LLM_DB_FACTORY_CATEGORY,
        "setting_selected_category": LLM_DB_GENERAL_CATEGORY,
        "setting_selected_name": LLM_SELECTED_CONFIGURATION,
    }

    status = setting_utils.put_nlp_setting(
        db,
        modelName=languageModelName,
        payload=payload,
        db_naming=db_naming,
        schemas=LLM_SCHEMAS,
    )

    # TODO: set cat language model!

    return status
