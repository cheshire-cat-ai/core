import os
import fnmatch

from fastapi import Request
from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader

from cat.looking_glass.stray_cat import StrayCat

API_KEY = [
    key.strip() for key in os.getenv("API_KEY", "").split("|") if key.strip()
]
"""List[str]: list of piped API keys.

The list stores all the API keys set in the `.env` file.
The keys are piped with a `|`, hence the list takes care of splitting and storing them.  
"""

api_key_header = APIKeyHeader(name="access_token", auto_error=False)


def check_api_key(request: Request, api_key: str = Security(api_key_header)) -> None | str:
    """Authenticate endpoint.

    Check the provided key is available in API keys list.

    Parameters
    ----------
    request : Request
        HTTP request.
    api_key : str
        API keys to be checked.

    Returns
    -------
    api_key : str | None
        Returns the valid key if set in the `.env`, otherwise return None.

    Raises
    ------
    HTTPException
        Error with status code `403` if the provided key is not valid.

    """
    if not API_KEY:
        return None
    if fnmatch.fnmatch(request.url.path, "/admin*"):
        return None
    if api_key in API_KEY:
        return api_key
    else:
        raise HTTPException(
            status_code=403,
            detail={"error": "Invalid API Key"}
        )


# get or create session (StrayCat)
def session(request: Request) -> StrayCat:

    strays = request.app.state.strays
    user_id = request.headers.get("user_id", "user")
    event_loop = request.app.state.event_loop
    
    if user_id not in strays.keys():
        strays[user_id] = StrayCat(user_id=user_id, main_loop=event_loop)
    return strays[user_id]