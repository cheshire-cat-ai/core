from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

def mount_public_spa(app: FastAPI):
    """
    Serves the SPA index.html file while allowing StaticFiles to handle the assets.
    """
    @app.get("/public")
    @app.get("/public/{path:path}")
    def serve_spa(path: str = ""):
        # Serve the main SPA index.html file
        index_file_path = os.path.join("/app/cat/public/", "index.html")
        with open(index_file_path, "r") as html_file:
            html_content = html_file.read()
        return HTMLResponse(content=html_content, media_type="text/html")

def mount(cheshire_cat_api: FastAPI):
    """
    Mount the SPA and configure StaticFiles to handle static assets.
    """
    # Mount the static files directory
    cheshire_cat_api.mount(
        "/public", StaticFiles(directory="/app/cat/public/"), name="static"
    )
    
    # Mount the main SPA serving logic
    mount_public_spa(cheshire_cat_api)