
from cat.auth.permissions import AuthPermission, AuthResource
from cat.auth.connection import WebSocketAuth
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from fastapi.concurrency import run_in_threadpool

from cat.looking_glass.stray_cat import StrayCat

router = APIRouter()

async def handle_messages(websocket: WebSocket, stray: StrayCat):

    while True:

        # Receive the next message from the WebSocket.
        user_message = await websocket.receive_json()

        # http endpoints may have been called while waiting for a message
        stray.load_working_memory_from_cache()

        # Run the `stray` object's method in a threadpool since it might be a CPU-bound operation.
        await run_in_threadpool(stray.run, user_message, return_message=False)


@router.websocket("/ws")
@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    stray=Depends(WebSocketAuth(AuthResource.CONVERSATION, AuthPermission.WRITE)),
):

    # Establish connection
    await websocket.accept()

    # Add the new WebSocket connection to the manager.
    websocket_manager = websocket.scope["app"].state.websocket_manager
    websocket_manager.add_connection(stray.user_id, websocket)

    try:
        # Process messages
        await handle_messages(websocket, stray)
    except WebSocketDisconnect:
        
        # stray's working memory in this scope has not been updated
        stray.load_working_memory_from_cache()
        
        # Remove connection on disconnect
        websocket_manager.remove_connection(stray.user_id)