from fastapi import APIRouter

from .points import router as points_router
from .collections import router as collections_router
from .convo_history import router as convo_history_router

memory_router = APIRouter()

memory_router.include_router(points_router, tags=["Vector Memory - Points"])
memory_router.include_router(collections_router, tags=["Vector Memory - Collections"])
memory_router.include_router(convo_history_router, tags=["Working Memory - Current Conversation"])
