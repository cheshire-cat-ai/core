from fastapi import APIRouter, Depends, Request, Body, Query
from typing import Dict
import tomli
from cat.auth.utils import AuthPermission, AuthResource 
from cat.auth.headers import http_auth

from cat.convo.messages import CatMessage

router = APIRouter()


# server status
@router.get("/")
async def home(
    stray = Depends(http_auth(AuthResource.STATUS, AuthPermission.READ))
) -> Dict:
    """Server status""" 
    with open("pyproject.toml", "rb") as f:
        project_toml = tomli.load(f)["project"]

    return {
        "status": "We're all mad here, dear!",
        "version": project_toml['version']
    }


@router.post("/message", response_model=CatMessage)
async def message_with_cat(
    payload: Dict = Body({"text": "hello!"}),
    stray = Depends(http_auth(AuthResource.CONVERSATION, AuthPermission.WRITE)),
) -> Dict:
    """Get a response from the Cat"""
    answer = await stray({"user_id": stray.user_id, **payload})
    return answer