from typing import Any, Dict, List, Optional, TypedDict
from pydantic import BaseModel

class ResponseDelete(BaseModel):
    deleted: Any

class Collection(BaseModel):
    name: str
    vectors_count: int

class ResponseCollections(BaseModel):
    collections: List[Collection]

class RecallCollection(BaseModel):
    id: str
    score: float
    vector: List[int]

class Vector(BaseModel):
    embedder: str
    collections: Dict[str, RecallCollection]

class Query(BaseModel):
    text: str
    vector: List[int]

class ResponseMemoryRecall(BaseModel):
    query: Query
    vectors: Vector

class Conversation(BaseModel):
    who: str
    message: str

class ResponseConversationHistory(BaseModel):
    history: List[Conversation]