import asyncio
from enum import Enum
from cat.auth.utils import AuthPermission, AuthResource, AuthUserInfo
import jwt
from jwt.exceptions import InvalidTokenError

from fastapi import (
    WebSocket,
    Request,
)
from fastapi import Security, HTTPException, WebSocketException
from fastapi.security.api_key import APIKeyHeader

from cat.looking_glass.stray_cat import StrayCat
from cat.env import get_env
from cat.log import log


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


async def authorize_user_from_token(token: str, auth_resource: AuthResource, auth_permission: AuthPermission) -> AuthUserInfo | None:

    # Auth check for legacy admin
    if not is_jwt(token):
        environment_api_key = get_env("CCAT_API_KEY")
        if token == environment_api_key:
            return AuthUserInfo(
                user_id="admin",
                user_data={}
            )

    try:
        # decode token
        payload = jwt.decode(
            token,
            get_env("CCAT_JWT_SECRET"),
            algorithms=[get_env("CCAT_JWT_ALGORITHM")]
        )

        # TODOAUTH: verify token expiration

        # build a user info obj that core can understand
        return AuthUserInfo(
            user_id=payload["username"],
            user_data=payload # TODOAUTH: maybe not the whole payload?
        )
    except Exception as e:
        log.error("Could not decode JWT")

    # do not pass
    return None



# TODOAUTH: test token and api_key both from Authorization and access_token header

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


def ws_auth(resource: AuthResource, permission: AuthPermission) -> None | StrayCat:
    async def ws_auth(
            websocket: WebSocket,
            user_id: str = "user",
            token: str | None = None,
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

        async def get_user_stray(user_info: AuthUserInfo):
            strays = websocket.app.state.strays

            user_id = user_info.user_id
            if user_id in strays.keys():
                stray = strays[user_id]       
                # Close previus ws connection
                if stray._StrayCat__ws:
                    await stray._StrayCat__ws.close()
                # Set new ws connection
                stray._StrayCat__ws = websocket 
                log.info(f"New websocket connection for user '{user_id}', the old one has been closed.")
                return stray
                
            else:
                stray = StrayCat(
                    ws=websocket,
                    user_id=user_id,
                    user_data=user_info.user_data,
                    main_loop=asyncio.get_running_loop()
                )
                strays[user_id] = stray
                return stray

        # try to get user from local idp
        local_user_info = await authorize_user_from_token(token, resource, permission)
        if local_user_info:
            # replace local_user_info id with websocket id
            log.info(local_user_info)
            local_user_info["user_id"] = user_id
            log.info(local_user_info)
            return await get_user_stray(local_user_info)

        # try to get user from auth_handler
        auth_handler = websocket.app.state.ccat.auth_handler
        auth_handler_user_info: AuthUserInfo = await auth_handler.authorize_user_from_token(token, resource, permission)
        if auth_handler_user_info:
            return await get_user_stray(auth_handler_user_info)
        
        raise WebSocketException(
            code=1004,
            reason="Invalid Credentials"
        )
    return ws_auth
  

def http_auth(resource: AuthResource, permission: AuthPermission) -> None | StrayCat:
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

        def get_user_stray(user_info: AuthUserInfo):
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
        
        credential = extract_credential(request)

        # try to get user from local idp
        local_auth = await authorize_user_from_token(credential, resource, permission) 
        if local_auth:
            return get_user_stray(local_auth)

        # try to get user from auth_handler
        auth_handler = request.app.state.ccat.auth_handler
        user_info: AuthUserInfo = await auth_handler.authorize_user_from_token(credential, resource, permission)
        if user_info:
            return get_user_stray(user_info)

        raise HTTPException(
            status_code=403,
            detail={"error": "Invalid Credentials"}
        )   
    return http_auth

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