import traceback
import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
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
        await run_in_threadpool(stray.run, user_message)


@router.websocket("/ws")
@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str = "user"):
    """
    Endpoint to handle incoming WebSocket connections by user id, process messages, and check for messages.
    """

    # Retrieve the `ccat` instance from the application's state.
    strays = websocket.app.state.strays

    # Skip the coroutine if the same user is already connected via WebSocket.
    if user_id in strays.keys():
        stray = strays[user_id]       
        # Close previus ws connection
        if stray._StrayCat__ws:
            await stray._StrayCat__ws.close()
        # Set new ws connection
        stray._StrayCat__ws = websocket 
        log.info(f"New websocket connection for user '{user_id}', the old one has been closed.")
        
    else:
        # Temporary conversation-based `cat` object as seen from hooks and tools.
        # Contains working_memory and utility pointers to main framework modules
        # It is passed to both memory recall and agent to read/write working memory
        stray = StrayCat(
            ws=websocket,
            user_id=user_id,
            main_loop=asyncio.get_running_loop()
        )
        strays[user_id] = stray

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



