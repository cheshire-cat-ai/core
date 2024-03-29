import traceback
import asyncio

from fastapi import APIRouter, WebSocketDisconnect, WebSocket
from fastapi.concurrency import run_in_threadpool

from cat.looking_glass.stray_cat import StrayCat
from cat.log import log
from cat import utils

router = APIRouter()

async def receive_message(websocket: WebSocket, stray: StrayCat):
    """
    Continuously receive messages from the WebSocket and forward them to the `ccat` object for processing.
    """

    while True:
        # Receive the next message from the WebSocket.
        user_message = await websocket.receive_json()
        user_message["user_id"] = stray.user_id

        # Run the `ccat` object's method in a threadpool since it might be a CPU-bound operation.
        cat_message = await run_in_threadpool(stray.run, user_message)

        # Send the response message back to the user.
        await websocket.send_json(cat_message)


async def check_messages(websocket: WebSocket, stray: StrayCat):
    """
    Periodically check if there are any new notifications from the `ccat` instance and send them to the user.
    """

    while True:
        # extract from FIFO list websocket notification
        notification = await stray._StrayCat__ws_messages.get()
        await websocket.send_json(notification)


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
        #await stray._ws.close() # REFACTOR: handle ws closing (coroutines remain open)
        stray.ws = websocket # ws connection is overwritten
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
        # Process messages and check for notifications concurrently.
        await asyncio.gather(
            receive_message(websocket, stray),
            check_messages(websocket, stray)
        )
    except WebSocketDisconnect:
        # Handle the event where the user disconnects their WebSocket.
        log.info("WebSocket connection closed")
    except Exception as e:
        # Log any unexpected errors and send an error message back to the user.
        log.error(e)
        traceback.print_exc()

        await websocket.send_json({
            "type": "error",
            "name": type(e).__name__,
            "description": utils.explicit_error_message(e)
        })
    # finally:
    #     del strays[user_id]



