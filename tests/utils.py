import shutil
from cat.types import Task, Message, TextContent


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
        root_dir = "tests/mocks/mock_plugin"
        base_dir = "./"
    else:
        root_dir = "tests/mocks/"
        base_dir = "mock_plugin"

    return shutil.make_archive(
        base_name="tests/mocks/mock_plugin",
        format="zip",
        root_dir=root_dir,
        base_dir=base_dir,
    )
