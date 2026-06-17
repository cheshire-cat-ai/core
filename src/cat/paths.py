import os

# NOTE: do not move this file out of root package folder
BASE_PATH    = os.path.dirname(os.path.abspath(__file__))
PROJECT_PATH = os.getcwd()
PLUGINS_PATH = os.path.join(PROJECT_PATH, "plugins")
DATA_PATH    = os.path.join(PROJECT_PATH, "data")
UPLOADS_PATH = os.path.join(DATA_PATH, "uploads")


# TODOV2: method join(sub_path) to get full path from subpath