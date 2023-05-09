from fastapi import APIRouter
from typing import Dict

router = APIRouter()


# server status
@router.get("/")
async def home() -> Dict:
    """Server status"""
    #TODO: ping to swagger UI
    return {"status": "We're all mad here, dear!"}
