from fastapi import Request, APIRouter
from cat.utils import log

router = APIRouter()

# GET plugins
@router.get("/")
async def list_available_plugins(request: Request):
    """List available plugins."""

    # access cat instance
    ccat = request.app.state.ccat

    # plugins are managed by the MadHatter class
    plugins = ccat.mad_hatter.plugins

    print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
    print(plugins, type(plugins))
    print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')

    return plugins
