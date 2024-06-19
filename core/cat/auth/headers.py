import jwt
from jwt.exceptions import InvalidTokenError

from fastapi import (
    WebSocket,
    Request,
)
from fastapi import Security, HTTPException, WebSocketException
from fastapi.security.api_key import APIKeyHeader

from cat.looking_glass.stray_cat import StrayCat
from cat.factory.custom_auth_handler import AuthUserInfo
from cat.env import get_env
from cat.log import log


# TODOAUTH: test token and api_key both from Authorization and access_token header

def is_jwt(token: str) -> bool:
    """
    Returns whether a given string is a JWT.
    """
    try:
        # Decode the JWT without verification to check its structure
        jwt.decode(token, options={"verify_signature": False})
        return True
    except InvalidTokenError:
        return False


async def ws_auth(
        websocket: WebSocket,
        user_id="user",
    ) -> None | StrayCat:
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

    return # TODOAUTH recover ws

    ccat = websocket.app.state.ccat
    strays = websocket.app.state.strays

    # Internal auth or custom auth must return True
    allowed = await ccat.auth_handler._is_ws_allowed(websocket)
    if not allowed:
        raise WebSocketException(
            code=1004,
            reason="Invalid Credentials"
        )


def extract_credential(request):
    """
    Get JWT token or api key passed with the request
    """

    # Proper Authorization header
    authorization_header = request.headers.get("Authorization")
    if authorization_header and ("Bearer " in authorization_header):
        return authorization_header.replace("Bearer ", "")
        
    # Legacy header to pass CCAT_API_KEY
    access_token_header = request.headers.get("access_token")
    if access_token_header:
        log.warning(
            "Deprecation Warning: `access_token` header will not be supported in v2."
            "Pass your token/key using the `Authorization: Bearer <token>` format."
        )
        return access_token_header

    # no token found
    return None    


async def http_auth(request: Request) -> None | StrayCat:
    """Authenticate endpoint.

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

    credential = extract_credential(request)

    auth_handler = request.app.state.ccat.auth_handler
    if is_jwt(credential):
        # decode token
        user_info: AuthUserInfo = await auth_handler.get_user_info_from_token(credential)
    else:
        # api_key (could be None).
        # check if api_key is correct

        # TODOAUTH: check env variable here

        user_id = request.headers.get("user_id", "user")
        user_info: AuthUserInfo = await auth_handler.get_user_info_from_api_key(credential, user_id)

    if user_info is None:
        # identity provider does not want this user to get in
        raise HTTPException(
            status_code=403,
            detail={"error": "Invalid Credentials"}
        )


async def frontend_auth(request: Request) -> None | StrayCat:
    """Authenticate the admin panle and other webapps / single page apps, with access token in GET query params.

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
        Redirects to login page.

    """

    token = request.query_params.get("access_token")
    if token:

        # decode token
        auth_handler = request.app.state.ccat.auth_handler
        user_info: AuthUserInfo = await auth_handler.get_user_info_from_token(token)
        
        if user_info:
            strays = request.app.state.strays
            event_loop = request.app.state.event_loop

            user_id = user_info.user_id        
            if user_id not in strays.keys():
                strays[user_id] = StrayCat(
                    user_id=user_id,
                    user_data=user_info.user_data,
                    main_loop=event_loop
                )
            return strays[user_id]

    # no token or invalid token, redirect to login
    raise HTTPException(
        status_code=307,
        headers={
            "Location": "/auth/login"
        }
    )


# get or create session (StrayCat)
# TODOAUTH: substitute this with http_auth
def session(request: Request) -> StrayCat:

    strays = request.app.state.strays
    user_id = request.headers.get("user_id", "user")
    event_loop = request.app.state.event_loop
    
    if user_id not in strays.keys():
        strays[user_id] = StrayCat(user_id=user_id, main_loop=event_loop)
    return strays[user_id]