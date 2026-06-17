import uvicorn
from urllib.parse import urlparse

from cat import config
from cat.scaffold import scaffolder

# RUN!
def main():

    # scaffold dev project with minimal folders (cat is used as a package)
    scaffolder.setup_project()

    # debugging utilities, to deactivate set `DEBUG = False` in config.py
    debug_config = {}
    if config.DEBUG:
        debug_config = {
            "reload": True,
            "reload_dirs": [
                config.BASE_PATH,
                config.PLUGINS_PATH
            ],
            "reload_includes": [
                "plugin.json"
            ]
        }

    # uvicorn running behind an https proxy
    proxy_pass_config = {}
    if config.HTTPS_PROXY_MODE:
        proxy_pass_config = {
            "proxy_headers": True,
            "forwarded_allow_ips": config.CORS_FORWARDED_ALLOW_IPS,
        }

    base_url = urlparse(config.URL)
    if base_url.port:
        port = base_url.port
    elif base_url.scheme == 'http':
        port = 80
    elif base_url.scheme == 'https':
        port = 443
    else:
        raise Exception(f"Cannot extract port from config.URL {config.URL}")

    uvicorn.run(
        "cat.startup:cheshire_cat_api",
        host="0.0.0.0",
        port=port,
        ws="none",
        use_colors=True,
        log_level=config.LOG_LEVEL.lower(),
        **debug_config,
        **proxy_pass_config,
    )

if __name__ == "__main__":
    main()
