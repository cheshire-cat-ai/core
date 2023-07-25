import websocket

class WSLogger:
    def __init__(self, address):
        self.ws = websocket.WebSocket()
        self.ws.connect(address)
    
    def send(self, message):
        self.ws.send(message)
    
    def send_gapped(self, message):
        self.ws.send("")
        self.ws.send(message)
        self.ws.send("")

ws_logger = WSLogger("ws://192.168.1.133:3001")