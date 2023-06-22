from fastapi import APIRouter, Request
from sqlalchemy.orm import Session
from cat.db.database import get_db_session

router = APIRouter()

# get default prompt settings
@router.get("/")
def get_default_prompt_settings(request: Request):
    ccat = request.app.state.ccat

    return ccat.default_prompt_settings
