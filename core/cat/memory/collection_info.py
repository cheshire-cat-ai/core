from typing import Mapping


class CollectionInfo:
    points_count: int = 0
    config: Mapping[str, Mapping[str, Mapping[str, int]]] = { "params": { "vectors": { "size": 0}}}
    
    def __init__(
        self,
        points_count: int,
        vector_size: int
    ) -> None:
        self.points_count = points_count
        self.config["params"]["vectors"]["size"] = vector_size