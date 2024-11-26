from fastapi import APIRouter, Depends, Body
from fastapi.concurrency import run_in_threadpool
from typing import Dict

from cat.auth.permissions import AuthPermission, AuthResource
from cat.auth.connection import HTTPAuth

from cat.convo.messages import CatMessage
from cat.utils import get_cat_version

router = APIRouter()


# server status
@router.get("/")
async def status(
    stray=Depends(HTTPAuth(AuthResource.STATUS, AuthPermission.READ)),
) -> Dict:
    """Server status"""
    return {"status": "We're all mad here, dear!", "version": get_cat_version()}


@router.post("/message", response_model=CatMessage)
async def message_with_cat(
    payload: Dict = Body({"text": "hello!"}),
    stray=Depends(HTTPAuth(AuthResource.CONVERSATION, AuthPermission.WRITE)),
) -> Dict:
    """Get a response from the Cat"""
    user_message_json = {"user_id": stray.user_id, **payload}
    answer = await run_in_threadpool(stray.run, user_message_json, True)
    return answer
