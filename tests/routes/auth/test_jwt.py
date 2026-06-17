import os
import pytest
import time
import jwt

from cat.env import get_env
from cat.auth import JWTHelper

from tests.utils import send_http_message

jwt_helper = JWTHelper()

JWT_ALGO = "HS256"

def test_is_jwt(client):
    assert not jwt_helper.is_jwt("not_a_jwt.not_a_jwt.not_a_jwt")

    actual_jwt = jwt.encode(
        {"username": "Alice"},
        "some_secret",
        algorithm=JWT_ALGO,
    )
    assert jwt_helper.is_jwt(actual_jwt)


# TODOV2: these tests depend on /auth/token and /users endpoints that don't exist yet
# def test_refuse_issue_jwt(client): ...
# def test_issue_jwt(client): ...
# def test_issue_jwt_for_new_user(client, admin_headers): ...
# def test_jwt_expiration(client): ...
# def test_jwt_imposes_user_id(client): ...
# def test_jwt_self_signature_passes(client, admin_headers): ...
# def test_jwt_self_signature_fails(client, admin_headers): ...
