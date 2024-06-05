import fnmatch
from typing import Annotated

from fastapi import (
    WebSocket,
    Request,
)
from fastapi import Security, HTTPException, WebSocketException
from fastapi.security.api_key import APIKeyHeader

from cat.looking_glass.stray_cat import StrayCat
from cat.env import get_env
from cat.log import log


async def ws_auth(
    websocket: WebSocket,
    user_id="user",
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
    WebsocketDisconnect
        Websocket disconnection

    """

    ccat = websocket.app.state.ccat
    strays = websocket.app.state.strays

    # Internal auth or custom auth must return True
    allowed = await ccat.auth_handler._is_ws_allowed(websocket)
    if not allowed:
        raise WebSocketException(
            code=1004,
            reason="Invalid Credentials"
        )


async def http_auth(request: Request) -> bool: # TODOAUTH: return stray?
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
    allowed = await ccat.auth_handler._is_http_allowed(request)
    if not allowed:
        raise HTTPException(
            status_code=403,
            detail={"error": "Invalid Credentials"}
        )


async def browser_auth(request: Request) -> bool: # TODOAUTH: return stray?
    """Authenticate the admin with access token.

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

    log.warning(request.query_params)

    token = request.query_params.get("access_token")
    if token:
        ccat = request.app.state.ccat

        # Internal auth or custom auth must return True
        allowed = await ccat.auth_handler.verify_token(token)
        if not allowed:
            raise HTTPException(
            status_code=307,
            headers={
                "Location": "/auth/login"
            }
        )

    # no token or invalid token, redirect to login
    #raise HTTPException(
    #    status_code=307,
    #    headers={
    #        "Location": "/auth/login"
    #    }
    #)


# get or create session (StrayCat)
def session(request: Request) -> StrayCat:

    strays = request.app.state.strays
    user_id = request.headers.get("user_id", "user")
    event_loop = request.app.state.event_loop
    
    if user_id not in strays.keys():
        strays[user_id] = StrayCat(user_id=user_id, main_loop=event_loop)
    return strays[user_id]