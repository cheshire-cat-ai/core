from fastapi import APIRouter
from typing import Dict
from cat.db.database import Database
import tomli


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
