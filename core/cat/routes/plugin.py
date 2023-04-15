from fastapi import Request, APIRouter
from cat.utils import log

router = APIRouter()


# GET plugins
@router.get("/")
async def recall_memories_from_text(request: Request):
    """List availabel plugins."""

    # access cat instance
    ccat = request.app.state.ccat

    # plugins are managed byt the MadHatter class
    mad_hatter = ccat.mad_hatter
    log(mad_hatter.hooks)
    log(mad_hatter.tools)

    return (
        {
            "status": "MEOW",
        },
    )
