from fastapi import Header, Security, Depends, HTTPException
from fastapi.security.api_key import APIKeyHeader
import os

API_KEY = [key.strip() for key in os.getenv("API_KEY", "").split("|") if key.strip()]
api_key_header = APIKeyHeader(name="access_token", auto_error=False)

def check_api_key(api_key: str = Security(api_key_header)):
    if not API_KEY:
        return None
    if api_key in API_KEY:
        return api_key
    else:
        raise HTTPException(status_code=403, detail="Invalid API Key")
