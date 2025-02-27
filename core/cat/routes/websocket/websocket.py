from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from fastapi.concurrency import run_in_threadpool


from cat.auth.permissions import AuthPermission, AuthResource
from cat.auth.connection import WebSocketAuth
from cat.looking_glass.stray_cat import StrayCat
from cat.log import log

router = APIRouter()

async def handle_messages(websocket: WebSocket, cat: StrayCat):

    while True:

        # Receive the next message from the WebSocket.
        user_message = await websocket.receive_json()

        # http endpoints may have been called while waiting for a message
        cat.load_working_memory_from_cache()

        # Run the `cat` object's method in a threadpool since it might be a CPU-bound operation.
        await run_in_threadpool(cat.run, user_message, return_message=False)


@router.websocket("/ws")
@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    cat=Depends(WebSocketAuth(AuthResource.CONVERSATION, AuthPermission.WRITE)),
):

    # Establish connection
    await websocket.accept()

    # Add the new WebSocket connection to the manager.
    websocket_manager = websocket.scope["app"].state.websocket_manager
    websocket_manager.add_connection(cat.user_id, websocket)

    try:
        # Process messages
        await handle_messages(websocket, cat)
    except WebSocketDisconnect:
        log.info(f"WebSocket connection closed for user {cat.user_id}")
    finally:
        
        # cat's working memory in this scope has not been updated
        #cat.load_working_memory_from_cache()
        
        # Remove connection on disconnect
        websocket_manager.remove_connection(cat.user_id)