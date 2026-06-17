import os
import pytest

from cat.config import Config
from cat import config as global_config


def test_defaults_present():
    # zero-config: values resolve from cat/defaults.py
    assert global_config.URL == "http://localhost:1865"
    assert global_config.API_URL == "http://localhost:1865/api/v2/"
    assert isinstance(global_config.DEBUG, bool)
    assert isinstance(global_config.JWT_EXPIRE_MINUTES, int)


def test_derived_paths_under_project():
    assert global_config.PLUGINS_PATH == os.path.join(global_config.PROJECT_PATH, "plugins")
    assert global_config.DATA_PATH == os.path.join(global_config.PROJECT_PATH, "data")
    assert global_config.UPLOADS_PATH == os.path.join(global_config.DATA_PATH, "uploads")


def test_read_only_at_runtime():
    with pytest.raises(AttributeError):
        global_config.URL = "http://nope"


def test_missing_attribute_raises():
    with pytest.raises(AttributeError):
        _ = global_config.DOES_NOT_EXIST


def test_no_config_file_uses_defaults(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # no config.py present
    cfg = Config()
    assert cfg.URL == "http://localhost:1865"
    assert cfg.JWT_SECRET == "meow_jwt"


def test_override_from_project_config(tmp_path, monkeypatch):
    (tmp_path / "config.py").write_text(
        "URL = 'http://0.0.0.0:9000'\n"
        "API_KEY = 'secret'\n"
    )
    monkeypatch.chdir(tmp_path)
    cfg = Config()
    # overridden values win
    assert cfg.URL == "http://0.0.0.0:9000"
    assert cfg.API_KEY == "secret"
    # derived values follow the override
    assert cfg.API_URL == "http://0.0.0.0:9000/api/v2/"
    # untouched values fall back to defaults
    assert cfg.JWT_SECRET == "meow_jwt"


def test_path_override_from_project_config(tmp_path, monkeypatch):
    custom = str(tmp_path / "my_plugins")
    (tmp_path / "config.py").write_text(f"PLUGINS_PATH = {custom!r}\n")
    monkeypatch.chdir(tmp_path)
    cfg = Config()
    assert cfg.PLUGINS_PATH == custom


def test_env_not_read_by_core(tmp_path, monkeypatch):
    # core must never parse the environment for settings
    monkeypatch.setenv("URL", "http://from-env:1234")
    monkeypatch.setenv("CCAT_URL", "http://from-env:1234")
    monkeypatch.chdir(tmp_path)  # no config.py to read it in
    cfg = Config()
    assert cfg.URL == "http://localhost:1865"


def test_project_config_may_read_env(tmp_path, monkeypatch):
    # config.py is plain Python, so the project itself can opt into env reading
    monkeypatch.setenv("MY_URL", "http://from-env:4321")
    (tmp_path / "config.py").write_text(
        "import os\n"
        "URL = os.environ['MY_URL']\n"
    )
    monkeypatch.chdir(tmp_path)
    cfg = Config()
    assert cfg.URL == "http://from-env:4321"
