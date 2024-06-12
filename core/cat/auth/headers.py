import asyncio
from cat.auth.utils import AuthPermission, AuthResource, AuthUserInfo
from fastapi import (
    WebSocket,
    Request,
)
from fastapi import HTTPException, WebSocketException
from cat.looking_glass.stray_cat import StrayCat
from cat.log import log
from urllib.parse import parse_qs


async def http_extract_credential(request: Request) -> str | None:
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

async def ws_extract_credential(websocket: WebSocket) -> AuthUserInfo | None:
    """
    Extract token from WebSocket query string
    """
    query_params = parse_qs(websocket.url.query)
    return query_params.get("token", [None])[0]


def ws_auth(resource: AuthResource, permission: AuthPermission) -> None | StrayCat:
    """ws_auth factory.

        Parameters
        ----------
        resource : AuthResource
            requested resource.
        permission : AuthPermission
            requested permission.

        Returns
        -------
        StrayCat
            Authorized user's StrayCat instance.

        Raises
        ------
        WebsocketDisconnect
            Websocket disconnection

        """
    async def ws_auth(
            websocket: WebSocket
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


        # extract credential from request
        credential = await ws_extract_credential(websocket)

        # try to get user from local idp
        core_auth_handler = websocket.app.state.ccat.core_auth_handler
        local_user_info = await core_auth_handler.authorize_user_from_token(credential, resource, permission)
        if local_user_info:
            return await get_user_stray(local_user_info)

        # try to get user from auth_handler
        custom_auth_handler = websocket.app.state.ccat.custom_auth_handler
        auth_handler_user_info: AuthUserInfo = await custom_auth_handler.authorize_user_from_token(credential, resource, permission)
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
        
        # extract credential from request
        credential = await http_extract_credential(request)

        # try to get user from local idp
        core_auth_handler = request.app.state.ccat.core_auth_handler
        local_auth = await core_auth_handler.authorize_user_from_token(credential, resource, permission) 
        if local_auth:
            return get_user_stray(local_auth)

        # try to get user from auth_handler
        custom_auth_handler = request.app.state.ccat.custom_auth_handler
        user_info: AuthUserInfo = await custom_auth_handler.authorize_user_from_token(credential, resource, permission)
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