import os
import uvicorn
from dotenv import load_dotenv
from urllib.parse import urlparse

from cat import urls, paths
from cat.scaffold import scaffolder
from cat.env import get_env, get_env_bool

# RUN!
def main():

    # load env variables
    load_dotenv(dotenv_path=os.path.join(
        paths.PROJECT_PATH, ".env"
    ))
    # TODOV2: make sure this works also when distributed as a docker image

    # scaffold dev project with minimal folders (cat is used as a package)
    scaffolder.setup_project()

    # debugging utilities, to deactivate put `DEBUG=false` in .env
    debug_config = {}
    if get_env_bool("CCAT_DEBUG"):
        debug_config = {
            "reload": True,
            "reload_dirs": [
                paths.BASE_PATH,
                paths.PLUGINS_PATH
            ],
            "reload_includes": [
                "plugin.json"
            ]
        }

    # uvicorn running behind an https proxy
    proxy_pass_config = {}
    if get_env("CCAT_HTTPS_PROXY_MODE") in ("1", "true"): # TODOV2: is this necessary? can be the default?
        proxy_pass_config = {
            "proxy_headers": True,
            "forwarded_allow_ips": get_env("CCAT_CORS_FORWARDED_ALLOW_IPS"),
        }

    base_url = urlparse(urls.BASE_URL)
    if base_url.port:
        port = base_url.port
    elif base_url.scheme == 'http':
        port = 80
    elif base_url.scheme == 'https':
        port = 443
    else:
        raise Exception(f"Cannot extract port from CCAT_URL {urls.BASE_URL}")

    uvicorn.run(
        "cat.startup:cheshire_cat_api",
        host="0.0.0.0",
        port=port,
        ws="none",
        use_colors=True,
        log_level=get_env("CCAT_LOG_LEVEL").lower(),
        **debug_config,
        **proxy_pass_config,
    )

if __name__ == "__main__":
    main()
