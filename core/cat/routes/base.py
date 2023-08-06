from fastapi import APIRouter
from typing import Dict
from cat.db.database import Database
import tomli


router = APIRouter()


# server status
@router.get("/")
async def home() -> Dict:
    """Server status""" 
    project_toml = tomli.load(open("pyproject.toml", "rb"))["project"]

    return {
        "status": "We're all mad here, dear!",
        "version": project_toml['version']
    }
