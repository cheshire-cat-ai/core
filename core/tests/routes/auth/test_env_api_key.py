import os
import pytest
from tests.utils import send_websocket_message


# utility to make http requests with some headers
def http_request(client, headers={}):
    response = client.get("/", headers=headers)
    return response.status_code, response.json()


@pytest.mark.parametrize("header_name", ["Authorization", "access_token"])
def test_api_key_http(client, header_name):

    # set CCAT_API_KEY
    os.environ["CCAT_API_KEY"] = "meow_http"

    # add "Bearer: " when using `Authorization` header
    key_prefix = ""
    if header_name == "Authorization":
        key_prefix = "Bearer "

    wrong_headers = [
        {}, # no key
        { header_name: f"{key_prefix}wrong" }, # wrong key
        { header_name: f"{key_prefix}meow_ws" }, # websocket key
    ]

    # all the previous headers result in a 403
    for headers in wrong_headers:
        status_code, json = http_request(client, headers)
        assert status_code == 403
        assert json["detail"]["error"] == "Invalid Credentials"

    # allow access if CCAT_API_KEY is right
    headers = {header_name: f"{key_prefix}meow_http"}
    status_code, json = http_request(client, headers)
    assert status_code == 200
    assert json["status"] == "We're all mad here, dear!"

    # allow websocket access without any key
    mex = {"text": "Where do I go?"}
    res = send_websocket_message(mex, client)
    assert "You did not configure" in res["content"]

    # remove CCAT_API_KEY
    del os.environ["CCAT_API_KEY"]


def test_api_key_ws(client):

    # set CCAT_API_KEY_WS
    os.environ["CCAT_API_KEY_WS"] = "meow_ws"

    mex = {"text": "Where do I go?"}

    wrong_query_params = [
        {}, # no key
        { "token": "wrong" }, # wrong key
    ]

    for params in wrong_query_params:
        with pytest.raises(Exception) as e_info:
            res = send_websocket_message(mex, client, query_params=params)
        assert str(e_info.type.__name__) == "WebSocketDisconnect"

    # allow access if CCAT_API_KEY_WS is right
    query_params = {"token": "meow_ws"}
    res = send_websocket_message(mex, client, query_params=query_params)
    assert "You did not configure" in res["content"]

    # allow http access without any key
    status_code, json = http_request(client)
    assert status_code == 200
    assert json["status"] == "We're all mad here, dear!"

    # remove CCAT_API_KEY_WS
    del os.environ["CCAT_API_KEY_WS"]

