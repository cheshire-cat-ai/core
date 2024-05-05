from fastapi import APIRouter, Depends, Body
from typing import Dict, List
import tomli

from cat.headers import session
from cat.log import log
from cat.looking_glass.stray_cat import StrayCat
from pydantic import BaseModel

# Default router
router_v1 = APIRouter()

# Router v2
router_v2 = APIRouter()

class HomeResponse(BaseModel):
    status: str
    version: str


class MemoryResponse(BaseModel):
    page_content: str
    type: str
    score: float
    id: str
    metadata: Dict[str,str|int|float]

class MessageWhyResponse(BaseModel):
    input: str
    intermediate_steps: List
    memory: Dict[str,List[MemoryResponse]]

class CatResponse(BaseModel):
    type: str
    content: str
    user_id: str
    why: MessageWhyResponse


def home() -> Dict:
    with open("pyproject.toml", "rb") as f:
        project_toml = tomli.load(f)["project"]

    return {
        "status": "We're all mad here, dear!",
        "version": project_toml['version']
    }


# server status
@router_v1.get("/", deprecated=True)
async def home_v1() -> Dict:
    """Server status""" 
    log.warning("Deprecated: This endpoint will be removed in the next major version.")
    return home()

@router_v2.get("/", response_model=HomeResponse, response_model_exclude_none=True)
async def home_v2():
    """Server status""" 
    
    return home()


async def message_with_cat(
    payload: Dict,
    stray: StrayCat
) -> Dict:
    
    answer = await stray(payload)

    return answer


@router_v1.post("/message", deprecated=True)
async def message_with_cat_v1(
    payload: Dict = Body({"text": "hello!"}),
    stray = Depends(session),
) -> Dict:
    """Get a response from the Cat"""
    
    answer = await message_with_cat(payload, stray)
    log.warning("Deprecated: This endpoint will be removed in the next major version.")

    return answer

@router_v2.post("/message", response_model=CatResponse, response_model_exclude_none=True)
async def message_with_cat_v2(
    payload: Dict = Body({"text": "hello!"}),
    stray = Depends(session),
) -> Dict:
    """Get a response from the Cat"""
    
    answer = await message_with_cat(payload, stray)

    return answer