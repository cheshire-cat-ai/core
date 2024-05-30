
import os
from cat.env import get_supported_env_variables, get_env

def test_get_env(client):

    # container envs
    assert get_env("PYTHONUNBUFFERED") == "1"
    assert get_env("WATCHFILES_FORCE_POLLING") == "true"

    # unexisting
    assert get_env("UNEXISTING_ENV") == None
    assert get_env("CCAT_UNEXISTING_ENV") == None

    # set new
    os.environ["FAKE_ENV"] = "meow1"
    os.environ["CCAT_FAKE_ENV"] = "meow2"
    assert get_env("FAKE_ENV") == "meow1"
    assert get_env("CCAT_FAKE_ENV") == "meow2"

    # default env variables
    for k, v in get_supported_env_variables().items():
        assert get_env(k) == v
        # TODO: take away in v2
        # missing prefix (legacy)
        assert get_env(k.replace("CCAT_", "")) == v
    
