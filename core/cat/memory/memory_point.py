from typing import Iterable, Union, Optional, Dict, Any

class MemoryPoint:
    vector: Iterable
    id: Union[int, str]
    payload: Optional[Dict[str, Any]]

    def __init__(self, vector, id, payload=None):
        self.id = id
        self.payload = payload
        self.vector = vector