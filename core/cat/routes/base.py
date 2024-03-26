from fastapi import APIRouter, Depends, Request, Body, Query
from typing import Dict
import tomli
from cat.headers import session


router = APIRouter()


# server status
@router.get("/")
async def home() -> Dict:
    """Server status""" 
    with open("pyproject.toml", "rb") as f:
        project_toml = tomli.load(f)["project"]

    return {
        "status": "We're all mad here, dear!",
        "version": project_toml['version']
    }


@router.post("/message")
async def message_with_cat(
    request: Request,
    payload: Dict = Body({"text": "hello!"}),
    save: bool = Query(description="Decide whether to save the message or not to the chat history", default=False),
    stray = Depends(session),
) -> Dict:
    """Get a response from the Cat"""
    
    answer = await stray(message=payload, save=save)

    return answer