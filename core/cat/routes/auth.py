
from typing import Dict
import asyncio
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Request, Body, Query, HTTPException

from cat.auth.jwt import create_access_token
from cat.log import log

router = APIRouter()

class UserCredentials(BaseModel):
    user_name: str
    password: str

class JWTResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/token")
async def get_access_token(creds: UserCredentials):

    # TODOAUTH: have credentials in DB
    if creds.user_name == "admin" and creds.password == "admin":
        access_token = create_access_token({
            "sub": creds.user_name
        })
        return JWTResponse(access_token=access_token)
    
    # credentials are wrong, wait a second (for brute force attacks) and then reply with error
    await asyncio.sleep(1)
    raise HTTPException(
            status_code=401,
            detail={
                "error": f"Invalid Credentials"
            }
        )
