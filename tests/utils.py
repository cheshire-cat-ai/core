import os
import shutil

# Anchor mock paths to this file, not the cwd: tests run against a temp project
# folder (see the harness), so cwd-relative paths no longer resolve.
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
MOCKS_DIR = os.path.join(TESTS_DIR, "mocks")


def get_mock_plugin_info():
    """Decorated objects the mock plugin exposes, per the v2 Plugin model.

    v2 plugins collect hooks, endpoints and services (no `tools`/`forms` lists —
    those concepts were removed from the Plugin in core). Counts mirror
    `tests/mocks/mock_plugin/`:
      - 2 hooks   (`mock_hook` + `nested_folder/mock_another_hook`)
      - 7 endpoints (`mock_endpoint`)
      - 1 service (`models/mock_llm.MockModelProvider`)
    """
    return {
        "id": "mock_plugin",
        "hooks": 2,
        "endpoints": 7,
        "services": 1,
    }


def send_http_message(msg, client, agent="default", streaming=False, headers={}):
    """Send a chat message to an agent and return its TaskResult json.

    v2 chat goes through `POST /agents/{slug}/message` (there is no `/chat`
    route). For convenience the returned dict also carries a flattened `text`
    key: the concatenated text of the last assistant message.
    """
    res = client.post(
        f"/agents/{agent}/message",
        headers=headers,
        json={
            "messages": [
                {"role": "user", "content": [{"type": "text", "text": str(msg)}]}
            ],
            "stream": streaming,
        },
    )

    assert res.status_code == 200, res.text
    body = res.json()

    # flatten the last assistant message's text for easy assertions
    text = ""
    for message in reversed(body.get("messages", [])):
        if message.get("role") == "assistant":
            text = message.get("text", "")
            break
    body["text"] = text
    return body


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
