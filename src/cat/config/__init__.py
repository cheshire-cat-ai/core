"""
Configuration loader.

Resolves the single, read-only `config` object used across core: it starts from
the defaults in `cat.config.defaults`, then overrides any UPPERCASE constant redefined
in a `config.py` found in the project folder (current working directory).

Project paths and derived URLs are computed once here and exposed on the same
object, so there is no import-time global scattered across modules.

Usage:
    from cat import config
    config.URL
    config.PLUGINS_PATH
"""

import os
import importlib.util

from . import defaults


def _uppercase_constants(module) -> dict:
    """Collect UPPERCASE module-level constants from a module."""
    return {k: getattr(module, k) for k in dir(module) if k.isupper()}


class Config:
    """Read-only, merged configuration.

    Settings are accessed as attributes (e.g. `config.URL`). The object is frozen
    after construction; assigning to an attribute at runtime raises an error.
    """

    def __init__(self):
        # 1. start from core defaults
        values = _uppercase_constants(defaults)

        # 2. the project folder is the current working directory
        project_path = os.getcwd()

        # 3. override with the project's ./config.py if present (plain Python)
        user_config = self._load_user_config(project_path)
        if user_config is not None:
            values.update(_uppercase_constants(user_config))

        # 4. derived project paths (overridable: only filled if not set by the user)
        values.setdefault("PROJECT_PATH", project_path)
        values.setdefault("PLUGINS_PATH", os.path.join(values["PROJECT_PATH"], "plugins"))
        values.setdefault("DATA_PATH", os.path.join(values["PROJECT_PATH"], "data"))
        values.setdefault("UPLOADS_PATH", os.path.join(values["DATA_PATH"], "uploads"))

        # package installation directory (not overridable): the `cat` package
        # root, where `scaffold/` and `welcome.txt` live. `config` is a subpackage,
        # so go one level up from this file's directory.
        values["BASE_PATH"] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # freeze
        object.__setattr__(self, "_values", values)

    @staticmethod
    def _load_user_config(project_path):
        """Import ./config.py from the project folder, if it exists."""
        path = os.path.join(project_path, "config.py")
        if not os.path.exists(path):
            return None
        spec = importlib.util.spec_from_file_location("cat_user_config", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def __getattr__(self, name):
        try:
            return object.__getattribute__(self, "_values")[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        raise AttributeError("config is read-only")


config = Config()
