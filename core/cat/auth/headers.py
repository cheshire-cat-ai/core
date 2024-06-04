import fnmatch
from typing import Annotated

from fastapi import (
    WebSocket,
    Request,
)
from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader

from cat.looking_glass.stray_cat import StrayCat
from cat.env import get_env
from cat.log import log


def ws_auth(
    websocket: WebSocket,
    ) -> None | str: # TODOAUTH: return stray?
    """Authenticate websocket connection.

    Parameters
    ----------
    websocket : WebSocket
        Websocket connection.

    Returns
    -------
    None
        Does not raise an exception if the message is allowed.

    Raises
    ------
    HTTPException
        Error with status code `403` if the message is not allowed. # TODOAUTH: ws has no status code

    """

    ccat = websocket.app.state.ccat

    # Internal auth or custom auth must return True
    allowed = ccat.core_auth.is_ws_allowed(websocket) or ccat.authorizator.is_ws_allowed(websocket)
    if not allowed:
        raise HTTPException(
            status_code=403,
            detail={"error": "Invalid Credentials"}
    )

    
def http_auth(request: Request) -> bool: # TODOAUTH: return stray?
    """Authenticate endpoint.

    Check the provided key is available in API keys list.

    Parameters
    ----------
    request : Request
        HTTP request.

    Returns
    -------
    None
        Does not raise an exception if the request is allowed.

    Raises
    ------
    HTTPException
        Error with status code `403` if the request is not allowed.

    """

    ccat = request.app.state.ccat

    # Internal auth or custom auth must return True
    allowed = ccat.core_auth.is_http_allowed(request) or ccat.authorizator.is_http_allowed(request)
    if not allowed:
        raise HTTPException(
            status_code=403,
            detail={"error": "Invalid Credentials"}
    )


# get or create session (StrayCat)
def session(request: Request) -> StrayCat:

    strays = request.app.state.strays
    user_id = request.headers.get("user_id", "user")
    event_loop = request.app.state.event_loop
    
    if user_id not in strays.keys():
        strays[user_id] = StrayCat(user_id=user_id, main_loop=event_loop)
    return strays[user_id]