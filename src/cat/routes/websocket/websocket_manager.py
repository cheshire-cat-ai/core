from fastapi.websockets import WebSocket


class WebsocketManager:

    def __init__(self):

        # Keep connections in dictionary: user_id -> WebSocket
        self.connections = {}

    def add_connection(self, id: str, websocket: WebSocket):
        """Add a new WebSocket connection"""
        
        self.connections[id] = websocket

    def get_connection(self, id: str) -> WebSocket:
        """Retrieve a WebSocket connection by user id"""
        
        return self.connections.get(id, None)

    def remove_connection(self, id: str):
        """Remove a WebSocket connection by user id"""

        if id in self.connections:
            del self.connections[id]


