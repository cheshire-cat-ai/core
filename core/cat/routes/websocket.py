import traceback
import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from cat.log import log
from fastapi.concurrency import run_in_threadpool

from typing import Callable, Coroutine

from cat.looking_glass.ws_logger import ws_logger
from cat.looking_glass.utils import gen_response

import asyncio
import json

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.is_flow_diverted = False
        self.lock = True
        self.previous_bounded_flow = None

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
    
    async def send_string(self, message: str, websocket: WebSocket):
        await websocket.send_json(gen_response(message))

    async def send_string_unknown_ws(self, message: str):
        for connection in self.active_connections:
            await self.send_string(message, connection)

    def bind(self, function: Callable[[str, WebSocket], None]) -> None:
        self.binded_flow = function
        self.lock = True
    
    def divert_flow(self, function: Callable[[str, WebSocket], None]) -> None:
        self.is_flow_diverted = True
        self.binded_flow = function
        self.previous_bounded_flow = function
    
    def revert_flow(self) -> None:
        self.is_flow_diverted = False
        self.binded_flow = None
        self.previous_bounded_flow = None
    
    def is_new_binding(self) -> bool:
        return self.binded_flow != self.previous_bounded_flow


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

            manager.lock = True

            while manager.lock:

                if manager.is_flow_diverted:
                    # Custom logic
                    manager.lock = False

                    binded_flow = manager.binded_flow

                    await manager.binded_flow(user_message, websocket)

                    manager.previous_bounded_flow = binded_flow
                else:
                    # get response from the cat
                    cat_message = await run_in_threadpool(ccat, user_message)

                    # send output to specific user
                    await manager.send_personal_message(cat_message, websocket)

                    # if flow doesn't get diverted, run only this else condition.
                    # if it gets diverted during execution, it will rerun in the manager.is_flow_diverted clause.
                    if not manager.is_flow_diverted:
                        manager.lock = False

    async def check_notification():
        while True:
            # chat notifications (i.e. finished uploading)
            if len(ccat.web_socket_notifications) > 0:
                notification = ccat.web_socket_notifications[-1]
                ccat.web_socket_notifications = ccat.web_socket_notifications[:-1]
                await manager.send_personal_message(notification, websocket)

            await asyncio.sleep(1)  # wait for 1 seconds before checking againdas

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

