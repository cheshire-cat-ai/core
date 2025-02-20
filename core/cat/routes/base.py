from fastapi import APIRouter, Body
from fastapi.concurrency import run_in_threadpool
from typing import Dict
import tomli
from cat.auth.permissions import AuthPermission, AuthResource, check_permissions

from cat.convo.messages import CatMessage

router = APIRouter()


# server status
@router.get("/")
async def status(
    cat=check_permissions(AuthResource.STATUS, AuthPermission.READ),
) -> Dict:
    """Server status"""
    with open("pyproject.toml", "rb") as f:
        project_toml = tomli.load(f)["project"]

    return {"status": "We're all mad here, dear!", "version": project_toml["version"]}


@router.post("/message", response_model=CatMessage)
async def message_with_cat(
    payload: Dict = Body({"text": "hello!"}),
    cat=check_permissions(AuthResource.CONVERSATION, AuthPermission.WRITE),
) -> Dict:
    """Get a response from the Cat"""
    user_message_json = {"user_id": cat.user_id, **payload}
    answer = await run_in_threadpool(cat.run, user_message_json, True)
    return answer
