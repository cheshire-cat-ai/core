import os
import shutil


# utility function to communicate with the cat via websocket
def send_websocket_message(msg, client):

    with client.websocket_connect("/ws") as websocket:
        
        # sed ws message
        websocket.send_json(msg)

        # get reply
        reply = websocket.receive_json()
    
    return reply


# utility to send n messages via chat
def send_n_websocket_messages(num_messages, client):

    responses = []
    for m in range(num_messages):
        message = {
            "text": f"Red Queen {m}"
        }
        res = send_websocket_message(message, client)
        responses.append(res)

    return responses
            

def key_in_json(key, json):
    return key in json.keys()


def create_zip(zip_path):
    shutil.make_archive(
        zip_path,
        "zip",
        root_dir="tests/mocks/",
        base_dir="mock_plugin"
    )
    return zip_path

def delete_zip(zip_path):
    os.remove(zip_path)