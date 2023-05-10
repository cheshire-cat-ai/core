from fastapi import APIRouter
from typing import Dict

router = APIRouter()


# server status
@router.get("/")
async def home() -> Dict:
    """Server status"""
    return {"status": "We're all mad here, dear!"}
