import os
import shutil
import datetime
from uuid import uuid4

from cat.db import DB
from cat import paths


def setup_project():
    """
    Scaffold the project:
     - populate the database with initial settings.
     - create minimal project folders/files if they do not exist.
     - preinstall plugins if specified in env variable.
    """

    create_folders()
    populate_db()

def create_folders():
    """Create necessary folders if they do not exist."""

    scaffold_path = os.path.join(paths.BASE_PATH, "scaffold")

    for folder in ["data", "plugins"]:
        origin = os.path.join(scaffold_path, folder)
        destination = os.path.join(paths.PROJECT_PATH, folder)
        if not os.path.exists(destination):
            shutil.copytree(origin, destination)

def populate_db():
    """Init DB and insert minimal settings into it."""

    initial_settings = {
        "active_plugins": [],
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