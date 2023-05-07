from fastapi import APIRouter
from typing import Dict

router = APIRouter()


# server status
@router.get("/")
async def home() -> Dict:
    """Server status"""
    return {"status": "If you see this, the core is up!"}
