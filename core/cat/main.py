import uvicorn

from cat.env import get_env, fix_legacy_env_variables

# RUN!
if __name__ == "__main__":

    # TODO: take away in v2
    fix_legacy_env_variables()

    # debugging utilities, to deactivate put `DEBUG=false` in .env
    debug_config = {}
    if get_env("CCAT_DEBUG") == "true":
        debug_config = {
            "reload": True,
            "reload_includes": ["plugin.json"],
            "reload_excludes": ["*test_*.*", "*mock_*.*"],
        }
    # uvicorn running behind an https proxy
    proxy_pass_config = {}
    if get_env("CCAT_HTTPS_PROXY_MODE") in ("1", "true"):
        proxy_pass_config = {
            "proxy_headers": True,
            "forwarded_allow_ips": get_env("CCAT_CORS_FORWARDED_ALLOW_IPS"),
        }

    uvicorn.run(
        "cat.startup:cheshire_cat_api",
        host="0.0.0.0",
        port=80,
        use_colors=True,
        log_level=get_env("CCAT_LOG_LEVEL").lower(),
        **debug_config,
        **proxy_pass_config,
    )
