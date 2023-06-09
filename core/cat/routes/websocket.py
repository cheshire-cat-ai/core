import traceback
import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from cat.log import log

router = APIRouter()


# main loop via websocket
@router.websocket_route("/ws")
async def websocket_endpoint(websocket: WebSocket):
    ccat = websocket.app.state.ccat

    await websocket.accept()

    async def receive_message():
        while True:
            # message received from user
            user_message = await websocket.receive_json()

            # get response from the cat
            cat_message = ccat(user_message)

            # send output to user
            await websocket.send_json(cat_message)

    async def check_notification():
        while True:
            # chat notifications (i.e. finished uploading)
            if len(ccat.web_socket_notifications) > 0:
                notification = ccat.web_socket_notifications[-1]
                ccat.web_socket_notifications = ccat.web_socket_notifications[:-1]
                await websocket.send_json(notification)

            await asyncio.sleep(1)  # wait for 1 seconds before checking again

    try:
        await asyncio.gather(receive_message(), check_notification())
    except WebSocketDisconnect:
        log("WebSocket connection closed", "INFO")
    except Exception as e:
        log(e, "ERROR")
        traceback.print_exc()

        # send error to user
        await websocket.send_json(
            {
                "error": True,
                "code": type(e).__name__,
            }
        )
