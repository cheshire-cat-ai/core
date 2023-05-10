import traceback

from fastapi import APIRouter, WebSocket
from cat.utils import log

router = APIRouter()


# main loop via websocket
@router.websocket_route("/ws")
async def websocket_endpoint(websocket: WebSocket):
    ccat = websocket.app.state.ccat

    await websocket.accept()

    try:
        while True:
            # message received from user
            user_message = await websocket.receive_json()

            # get response from the cat
            cat_message = ccat(user_message["text"])

            # send output to user
            await websocket.send_json(cat_message)

            # chat notifications (i.e. finished uploading)
            if len(ccat.web_socket_notifications) > 0:
                notification = ccat.web_socket_notifications[-1]
                ccat.web_socket_notifications = ccat.web_socket_notifications[:-1]
                await websocket.send_json(notification)

    except Exception as e:  # WebSocketDisconnect as e:
        log(e)
        traceback.print_exc()

        # send error to user
        await websocket.send_json(
            {
                "error": True,
                "code": type(e).__name__,
            }
        )
