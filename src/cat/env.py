import os

# TODOV2: get rid of this stuff and just ensure default values from main.py

def get_supported_env_variables():

    return {
        "CCAT_URL": "http://localhost:1865",
        "CCAT_SQL": "sqlite:///data/core/core.db", # TODOV2: db could be encrypted by default # postgresql+asyncpg://user:password@localhost/dbname
        "CCAT_API_KEY": None, # TODOV2: not sure about the None default
        "CCAT_JWT_SECRET": "meow_jwt",
        "CCAT_JWT_EXPIRE_MINUTES": str(60 * 24),  # JWT expires after 1 day
        "CCAT_DEBUG": "true",
        "CCAT_LOG_LEVEL": "INFO",
        "CCAT_HTTPS_PROXY_MODE": "false",
        "CCAT_CORS_FORWARDED_ALLOW_IPS": "*",
        "CCAT_CORS_ENABLED": "true",
        "CCAT_CORS_ALLOWED_ORIGINS": "*",
        "CCAT_TELEMETRY": "true",
        "CCAT_PREINSTALLED_PLUGINS": ",".join([
            "https://github.com/cheshire-cat-ai/llms",
            "https://github.com/cheshire-cat-ai/ui",
            #"https://github.com/cheshire-cat-ai/uploads",
        ]),
    }


def get_env(name) -> str | None:
    """
    Utility to get environment variables. To be used only for supported Cat envs.
    Covers default supported variables and their default value
    """

    cat_default_env_variables = get_supported_env_variables()

    if name in cat_default_env_variables:
        default = cat_default_env_variables[name]
    else:
        default = None

    return os.getenv(name, default)


def get_env_bool(name) -> bool:
    """Check if an env variable is truthy (True, true, 1)."""
    return get_env(name) in ("true", "True", "1")
