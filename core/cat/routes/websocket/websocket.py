
from cat.auth.permissions import AuthPermission, AuthResource
from cat.auth.connection import WebSocketAuth
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from fastapi.concurrency import run_in_threadpool

from cat.looking_glass.stray_cat import StrayCat
from cat.routes.websocket.websocket_manager import WebsocketManager

# handles ws connections
websocket_manager = WebsocketManager()

router = APIRouter()

async def handle_messages(websocket: WebSocket, user_data):

    while True:
        # Receive the next message from the WebSocket.
        user_message = await websocket.receive_json()
        
        # Create a new stray for each message received, as it happens for http endpoints
        stray = StrayCat(user_data)

        # Run the `stray` object's method in a threadpool since it might be a CPU-bound operation.
        await run_in_threadpool(stray.run, user_message, return_message=False)
        del stray


@router.websocket("/ws")
@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    stray=Depends(WebSocketAuth(AuthResource.CONVERSATION, AuthPermission.WRITE)),
):

    # keep reference to user but drop the stray
    # (working memory is stored in cache so it's not lost)
    user_data = stray.user_data
    del stray

    # Establish connection
    await websocket.accept()

    # Add the new WebSocket connection to the manager.
    websocket_manager.add_connection(user_data.name, websocket) # TODOV2: use id

    try:
        # Process messages
        await handle_messages(websocket, user_data)
    except WebSocketDisconnect:
        # Remove connection on disconnect
        websocket_manager.remove_connection(user_data.name) # TODOV2: use id