from fastapi import APIRouter, Depends, Body
from typing import Dict
import tomli
from cat.auth.permissions import AuthPermission, AuthResource
from cat.auth.connection import HTTPAuth

from cat.convo.messages import CatMessage

router = APIRouter()


# server status
@router.get("/")
async def status(
    stray=Depends(HTTPAuth(AuthResource.STATUS, AuthPermission.READ)),
) -> Dict:
    """Server status"""
    with open("pyproject.toml", "rb") as f:
        project_toml = tomli.load(f)["project"]

    return {"status": "We're all mad here, dear!", "version": project_toml["version"]}


@router.post("/message", response_model=CatMessage)
async def message_with_cat(
    payload: Dict = Body({"text": "hello!"}),
    stray=Depends(HTTPAuth(AuthResource.CONVERSATION, AuthPermission.WRITE)),
) -> Dict:
    """Get a response from the Cat"""
    payload["user_id"] = stray.user_id
    return await stray.__call__(payload)
