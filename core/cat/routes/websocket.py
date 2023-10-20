import traceback
import asyncio
from cat.looking_glass.cheshire_cat import CheshireCat
from typing import Dict, Optional
from fastapi import APIRouter, WebSocketDisconnect, WebSocket
from cat.log import log
from fastapi.concurrency import run_in_threadpool

router = APIRouter()

# This constant sets the interval (in seconds) at which the system checks for notifications.
QUEUE_CHECK_INTERVAL = 1  # seconds


class ConnectionManager:
    """
    Manages active WebSocket connections.
    """

    def __init__(self):
        # List to store all active WebSocket connections.
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str = "user"):
        """
        Accept the incoming WebSocket connection and add it to the active connections list.
        """
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, ccat: CheshireCat, user_id: str = "user"):
        """
        Remove the given WebSocket from the active connections list.
        """
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in ccat.ws_messages:
            del ccat.ws_messages[user_id]

    async def send_personal_message(self, message: str, user_id: str = "user"):
        """
        Send a personal message (in JSON format) to the specified WebSocket.
        """
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)

    async def broadcast(self, message: str):
        """
        Send a message to all active WebSocket connections.
        """
        for connection in self.active_connections.values():
            await connection.send_json(message)


manager = ConnectionManager()


async def receive_message(ccat: CheshireCat, user_id: str = "user"):
    """
    Continuously receive messages from the WebSocket and forward them to the `ccat` object for processing.
    """
    while True:
        # Receive the next message from the WebSocket.
        user_message = await manager.active_connections[user_id].receive_json()

        # Run the `ccat` object's method in a threadpool since it might be a CPU-bound operation.
        cat_message = await run_in_threadpool(ccat, user_message)

        # Send the response message back to the user.
        await manager.send_personal_message(cat_message, user_id)


async def check_messages(ccat: CheshireCat, user_id: str = "user"):
    """
    Periodically check if there are any new notifications from the `ccat` instance and send them to the user.
    """

    # Initialize a Queue if the user_id is not present in the dictionary.
    if user_id not in ccat.ws_messages:
        ccat.ws_messages[user_id] = asyncio.Queue()

    while True:
        # extract from websocket messages from user's queue
        notification = await ccat.ws_messages[user_id].get()
        await manager.send_personal_message(notification, user_id)


@router.websocket_route("/ws")
@router.websocket_route("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: Optional[str] = None):
    """
    Endpoint to handle incoming WebSocket connections by user id, process messages, and check for messages.
    """

    # Retrieve the `ccat` instance from the application's state.
    ccat = websocket.app.state.ccat

    # If no user id is specified, use "user" as the default.
    user_id = user_id or "user"

    if user_id in manager.active_connections:
        # If the user already has an active WebSocket connection, close it.
        await manager.active_connections[user_id].close()
        manager.disconnect(ccat, user_id)

    # Add the new WebSocket connection to the manager.
    await manager.connect(websocket, user_id)

    try:
        # Process messages and check for notifications concurrently.
        await asyncio.gather(
            receive_message(ccat, user_id),
            check_messages(ccat, user_id)
        )
    except WebSocketDisconnect:
        # Handle the event where the user disconnects their WebSocket.
        log.info("WebSocket connection closed")
    except Exception as e:
        # Log any unexpected errors and send an error message back to the user.
        log.error(e)
        traceback.print_exc()
        await manager.send_personal_message({
            "type": "error",
            "name": type(e).__name__,
            "description": str(e),
        }, user_id)
    finally:
        # Remove the WebSocket from the manager when the user disconnects.
        manager.disconnect(ccat, user_id)
