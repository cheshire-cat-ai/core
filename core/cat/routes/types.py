from typing import Any, Dict, List, Optional, TypedDict
from pydantic import BaseModel

class Vector(BaseModel):
    embedder: str
    collections: Dict[str, Any]

class ResponseMemoryRecall(BaseModel):
    query: Dict[str, Any]
    vectors: Vector