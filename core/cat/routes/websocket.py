import traceback
import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from cat.log import log
from fastapi.concurrency import run_in_threadpool

router = APIRouter()

# This constant sets the interval (in seconds) at which the system checks for notifications.
NOTIFICATION_CHECK_INTERVAL = 1  # seconds


class ConnectionManager:
    """
    Manages active WebSocket connections.
    """

    def __init__(self):
        # List to store all active WebSocket connections.
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """
        Accept the incoming WebSocket connection and add it to the active connections list.
        """
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """
        Remove the given WebSocket from the active connections list.
        """
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """
        Send a personal message (in JSON format) to the specified WebSocket.
        """
        await websocket.send_json(message)

    async def broadcast(self, message: str):
        """
        Send a message to all active WebSocket connections.
        """
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()


async def receive_message(websocket: WebSocket, ccat: object):
    """
    Continuously receive messages from the WebSocket and forward them to the `ccat` object for processing.
    """
    while True:
        user_message = await websocket.receive_json()

        # Run the `ccat` object's method in a threadpool since it might be a CPU-bound operation.
        cat_message = await run_in_threadpool(ccat, user_message)

        # Send the response message back to the user.
        await manager.send_personal_message(cat_message, websocket)


async def check_notification(websocket: WebSocket, ccat: object):
    """
    Periodically check if there are any new notifications from the `ccat` object and send them to the user.
    """
    while True:
        if ccat.ws_messages:
            # extract from FIFO list websocket notification
            notification = ccat.ws_messages.pop(0)
            await manager.send_personal_message(notification, websocket)

        # Sleep for the specified interval before checking for notifications again.
        await asyncio.sleep(NOTIFICATION_CHECK_INTERVAL)


@router.websocket_route("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Endpoint to handle incoming WebSocket connections, process messages, and check for notifications.
    """

    # Retrieve the `ccat` instance from the application's state.
    ccat = websocket.app.state.ccat

    # Add the new WebSocket connection to the manager.
    await manager.connect(websocket)

    try:
        # Process messages and check for notifications concurrently.
        await asyncio.gather(
            receive_message(websocket, ccat),
            check_notification(websocket, ccat)
        )
    except WebSocketDisconnect:
        # Handle the event where the user disconnects their WebSocket.
        log("WebSocket connection closed", "INFO")
    except Exception as e:
        # Log any unexpected errors and send an error message back to the user.
        log(e, "ERROR")
        traceback.print_exc()
        await manager.send_personal_message({
            "type": "error",
            "name": type(e).__name__,
            "description": str(e),
        }, websocket)
    finally:
        # Always ensure the WebSocket is removed from the manager, regardless of how the above block exits.
        manager.disconnect(websocket)
