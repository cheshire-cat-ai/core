import traceback
import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from cat.log import log

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

# main loop via websocket
@router.websocket_route("/ws")
async def websocket_endpoint(websocket: WebSocket):
    ccat = websocket.app.state.ccat

    await manager.connect(websocket)

    async def receive_message():
        while True:
            # message received from specific user
            user_message = await websocket.receive_json()

            # get response from the cat
            cat_message = ccat(user_message)

            # send output to specific user
            await manager.send_personal_message(cat_message, websocket)

    async def check_notification():
        while True:
            # chat notifications (i.e. finished uploading)
            if len(ccat.web_socket_notifications) > 0:
                notification = ccat.web_socket_notifications[-1]
                ccat.web_socket_notifications = ccat.web_socket_notifications[:-1]
                await manager.send_personal_message(notification, websocket)

            await asyncio.sleep(1)  # wait for 1 seconds before checking again

    try:
        await asyncio.gather(receive_message(), check_notification())
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        log("WebSocket connection closed", "INFO")
    except Exception as e:
        log(e, "ERROR")
        traceback.print_exc()

        # send error to specific user
        await manager.send_personal_message(
            {
                "type": "error",
                "name": type(e).__name__,
                "description": str(e),
            },
            websocket
        )
