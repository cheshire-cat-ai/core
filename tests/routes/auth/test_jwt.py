import jwt

from cat.auth import JWTHelper
from cat.auth.user import User
from cat import config


jwt_helper = JWTHelper()

JWT_ALGO = "HS256"


def test_is_jwt():
    assert not jwt_helper.is_jwt("not_a_jwt.not_a_jwt.not_a_jwt")

    actual_jwt = jwt.encode({"username": "Alice"}, "some_secret", algorithm=JWT_ALGO)
    assert jwt_helper.is_jwt(actual_jwt)


def test_encode_decode_roundtrip():
    from uuid import uuid4

    user = User(id=uuid4(), name="Alice", roles=["editor"])
    token = jwt_helper.encode(user)

    assert jwt_helper.is_jwt(token)

    payload = jwt_helper.decode(token)
    assert payload is not None
    assert payload["sub"] == str(user.id)
    assert payload["username"] == "Alice"
    assert payload["roles"] == ["editor"]


def test_decode_wrong_secret_returns_none():
    # a token signed with a different secret must not verify
    bad = jwt.encode({"sub": "x", "username": "y", "roles": []}, "not_the_secret", algorithm=JWT_ALGO)
    assert jwt_helper.decode(bad) is None


def test_decode_uses_configured_secret():
    # a token signed with the configured secret decodes
    good = jwt.encode({"sub": "x", "username": "y", "roles": []}, config.JWT_SECRET, algorithm=JWT_ALGO)
    payload = jwt_helper.decode(good)
    assert payload is not None
    assert payload["username"] == "y"
