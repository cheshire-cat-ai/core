from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()

class PromptSettings(BaseModel):
    prefix: str
    use_episodic_memory: bool
    use_declarative_memory: bool
    use_procedural_memory: bool

# get default prompt settings
@router.get("/")
def get_default_prompt_settings(request: Request) -> PromptSettings:
    ccat = request.app.state.ccat

    return ccat.default_prompt_settings
