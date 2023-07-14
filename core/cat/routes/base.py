from fastapi import APIRouter
from typing import Dict
from cat.db.database import Database

router = APIRouter()


# server status
@router.get("/")
async def home() -> Dict:
    """Server status"""
    db = Database()
    return {"status": db.all()}
