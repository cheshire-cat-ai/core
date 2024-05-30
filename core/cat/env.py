import os


def get_supported_env_variables():
    return {
        "CCAT_CORE_HOST": "localhost",
        "CCAT_CORE_PORT": "1865",
        "CCAT_CORE_USE_SECURE_PROTOCOLS": "",
        "CCAT_API_KEY": "",
        "CCAT_DEBUG": "true",
        "CCAT_LOG_LEVEL": "INFO",
        "CCAT_CORS_ALLOWED_ORIGINS": "",
        "CCAT_QDRANT_HOST": "",
        "CCAT_QDRANT_PORT": "6333",
        "CCAT_QDRANT_API_KEY": "",
        "CCAT_SAVE_MEMORY_SNAPSHOTS": "false",
        "CCAT_METADATA_FILE": "cat/data/metadata.json",
    }


# TODO: take away in v2
def fix_legacy_env_variables():
    
    cat_default_env_variables = get_supported_env_variables()

    for new_name, v in cat_default_env_variables.items():
        legacy_name = new_name.replace("CCAT_", "")
        legacy_value = os.getenv(legacy_name, False)
        if legacy_value:
            os.environ[new_name] = legacy_value


def get_env(name):
    """Utility to get an environment variable value. To be used only for supported Cat envs. 
    - covers default supported variables and their default value
    - automagically handles legacy env variables missing the prefix "CCAT_"
    """

    cat_default_env_variables = get_supported_env_variables()

    # TODO: take away in v2
    # support cat envs without the "CCAT_" prefix
    legacy_variables = {}
    for k, v in cat_default_env_variables.items():
        legacy_name = k.replace("CCAT_", "")
        legacy_variables[legacy_name] = v
    cat_default_env_variables = cat_default_env_variables | legacy_variables

    if name in cat_default_env_variables:
        default = cat_default_env_variables[name]
    else:
        default=None

    return os.getenv(name, default)