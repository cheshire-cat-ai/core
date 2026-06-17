import os
import shutil
import datetime
from uuid import uuid4

from cat.db import DB
from cat import config


def setup_project():
    """
    Scaffold the project:
     - create minimal project folders/files if they do not exist.
     - create the database and its tables.
     - populate the database with initial settings.
    """

    from cat.db.models import create_tables

    create_folders()
    create_tables()
    populate_db()

def installed_plugin_names():
    """Names of the plugin directories present in the project's `plugins/` folder.

    Read from disk *after* `create_folders()` has copied the vendored starters
    in, so the seeded active set always matches what is actually installed —
    never a dangling reference to a plugin that isn't on disk. On a fresh
    project this is exactly the starters just copied (e.g. ['chats', 'llms',
    'ui']). Files (like the plugin-authoring readme) are ignored; only plugin
    folders count.
    """
    plugins_path = config.PLUGINS_PATH
    if not os.path.isdir(plugins_path):
        return []
    return sorted(
        name
        for name in os.listdir(plugins_path)
        if os.path.isdir(os.path.join(plugins_path, name))
    )

def create_folders():
    """Create necessary folders if they do not exist."""

    scaffold_path = os.path.join(config.BASE_PATH, "scaffold")

    for folder in ["data", "plugins"]:
        origin = os.path.join(scaffold_path, folder)
        destination = os.path.join(config.PROJECT_PATH, folder)
        if not os.path.exists(destination):
            shutil.copytree(origin, destination)

def populate_db():
    """Init DB and insert minimal settings into it."""

    initial_settings = {
        # Seed the active plugins from the plugins actually present in the
        # project folder (the starters just copied in on a fresh install), so a
        # fresh install boots with a working LLM, UI and chats — and the seed
        # never points at a plugin that isn't on disk.
        "active_plugins": installed_plugin_names(),
        "installation_info": {
            "id": str(uuid4()),
            "alive_since": datetime.datetime.now(datetime.timezone.utc),
        },
    }

    # Note: scaffolder runs sync, but DB methods are async
    # This code runs during initial setup before async context is available
    # Keeping as-is for now, or convert to async if scaffolder supports it
    from cat.db.models import KeyValueDB

    for key, value in initial_settings.items():
        setting = KeyValueDB.objects().where(KeyValueDB.key == key).first().run_sync()
        if setting is None:
            setting = KeyValueDB(key=key, value=value)
            setting.save().run_sync()