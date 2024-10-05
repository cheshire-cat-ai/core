
from cat.auth.permissions import AuthPermission, AuthResource
from cat.auth.connection import WebSocketAuth
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from fastapi.concurrency import run_in_threadpool

from cat.looking_glass.stray_cat import StrayCat
from cat.log import log


router = APIRouter()


async def receive_message(websocket: WebSocket, stray: StrayCat):
    """
    Continuously receive messages from the WebSocket and forward them to the `ccat` object for processing.
    """

    while True:
        # Receive the next message from the WebSocket.
        user_message = await websocket.receive_json()
        user_message["user_id"] = stray.user_id

        # Run the `stray` object's method in a threadpool since it might be a CPU-bound operation.
        await run_in_threadpool(stray.run, user_message, return_message=False)


@router.websocket("/ws")
@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    stray=Depends(WebSocketAuth(AuthResource.CONVERSATION, AuthPermission.WRITE)),
):
    """
    Endpoint to handle incoming WebSocket connections by user id, process messages, and check for messages.
    """

    # Add the new WebSocket connection to the manager.
    await websocket.accept()
    try:
        # Process messages
        await receive_message(websocket, stray)
    except WebSocketDisconnect:
        # Handle the event where the user disconnects their WebSocket.
        stray._StrayCat__ws = None
        log.info("WebSocket connection closed")
    # finally:
    #     del strays[user_id]
