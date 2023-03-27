
from fastapi import APIRouter

router = APIRouter()

# server status
@router.get("/")
async def home():
    """Server status"""
    return {"status": "We're all mad here, dear!"}