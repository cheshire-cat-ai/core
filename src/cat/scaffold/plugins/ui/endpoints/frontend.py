import os
from fastapi import HTTPException
from fastapi.responses import FileResponse, HTMLResponse

from cat import endpoint
from cat.context import app


@endpoint.get("/", include_in_schema=False)
async def frontend_index() -> HTMLResponse:

    plugin = app().plugin

    index_path = os.path.abspath(
        os.path.join(plugin.path, "dist/index.html")
    )
    return FileResponse(path=index_path)


@endpoint.get("/assets/{path:path}", include_in_schema=False)
async def frontend_assets(path: str) -> HTMLResponse:

    plugin = app().plugin

    assets_path = os.path.abspath(
        os.path.join(plugin.path, "dist/assets")
    )

    file_path = os.path.abspath(os.path.join(assets_path, path))

    if not file_path.startswith(assets_path):
        raise HTTPException(status_code=403, detail="Access forbidden")

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path=file_path)
