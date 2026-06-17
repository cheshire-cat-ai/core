from fastapi import APIRouter
from .plugins_local import router as r_crud
from .plugins_registry import router as r_registry

router = APIRouter(tags=["Plugins"])
for r in [r_crud, r_registry]:
    router.include_router(r)
