import os
import shutil
from cat.types import Task, Message, TextContent

# Anchor mock paths to this file, not the cwd: tests run after chdir-ing into a
# temp project folder (see conftest), so cwd-relative paths no longer resolve.
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
MOCKS_DIR = os.path.join(TESTS_DIR, "mocks")


def get_core_plugins_ids():
    """Ids of the always-present plugins on a fresh install.

    In v2 the baseline is the scaffolded starters copied into the project's
    plugins folder (e.g. ['chats', 'llms', 'ui']), not a single 'core_plugin'
    like v1. Read from disk so the list tracks whatever the scaffolder ships.
    """
    from cat.scaffold.scaffolder import installed_plugin_names
    return installed_plugin_names()


def get_mock_plugin_info():
    return {
        "id": "mock_plugin",
        "hooks": 4,
        "tools": 1,
        "forms": 1,
        "endpoints": 7
    }

def get_request(msg="meow"):
    return Task(
        messages=[
            Message(
                role="user",
                content=[
                    TextContent(text=msg)
                ]
            )
        ],
        stream=False
    )

def send_http_message(
        msg,
        client,
        streaming=False,
        headers={}
    ):
    res = client.post(
        "/chat",
        headers=headers,
        json={
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": str(msg)}
                    ]
                }
            ],
            "stream": streaming
        }
    )

    assert res.status_code == 200
    return res.json()


# create a plugin zip out of the mock plugin folder.
# - Used to test plugin upload.
# - zip can be created flat (plugin files in root dir) or nested (plugin files in zipped folder)
def create_mock_plugin_zip(flat: bool):
    if flat:
        root_dir = os.path.join(MOCKS_DIR, "mock_plugin")
        base_dir = "./"
    else:
        root_dir = MOCKS_DIR
        base_dir = "mock_plugin"

    return shutil.make_archive(
        base_name=os.path.join(MOCKS_DIR, "mock_plugin"),
        format="zip",
        root_dir=root_dir,
        base_dir=base_dir,
    )
