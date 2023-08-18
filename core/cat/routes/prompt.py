from fastapi import APIRouter, Request

router = APIRouter()

# get default prompt settings
@router.get("/settings/")
def get_default_prompt_settings(request: Request):
    ccat = request.app.state.ccat

    return ccat.default_prompt_settings
