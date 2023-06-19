
# utility function to communicate with the cat via websocket
def send_websocket_message(msg, client):

    with client.websocket_connect("/ws") as websocket:
        
        # sed ws message
        websocket.send_json(msg)

        # get reply
        return websocket.receive_json()