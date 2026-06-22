"""
The per-user key-value store: the `UserStore` data layer and the ambient
`user` proxy (`from cat import user`) that sits on top of it.

The autouse `isolated_project` fixture gives every test a fresh SQLite DB.
"""

from uuid import uuid4, uuid5, NAMESPACE_DNS

import pytest

from cat.db import UserStore, store
from cat.ambient.context_vars import Ctx, use_ctx, user
from cat.auth.user import User


def _user(name: str) -> User:
    """A deterministic User (stable id per name), mirroring the context_vars tests."""
    return User(id=uuid5(NAMESPACE_DNS, name), name=name)


# Same matrix as the global store — the per-user layer must round-trip types too.
ROUNDTRIP_CASES = [
    ("int", 9),
    ("float", 3.14),
    ("str", "hello"),
    ("bool", True),
    ("none", None),
    ("list", [1, 2, 3]),
    ("empty_list", []),
    ("dict", {"a": 1}),
    ("nested", {"todos": [{"text": "buy milk", "done": False}]}),
]


# --- UserStore data layer --------------------------------------------------

@pytest.mark.parametrize("name,value", ROUNDTRIP_CASES, ids=[c[0] for c in ROUNDTRIP_CASES])
async def test_roundtrip_preserves_value_and_type(name, value):
    uid = uuid4()
    await UserStore.save(uid, name, value)
    loaded = await UserStore.load(uid, name)
    assert loaded == value
    assert type(loaded) is type(value)


async def test_number_comes_back_as_number():
    uid = uuid4()
    await UserStore.save(uid, "count", 9)
    loaded = await UserStore.load(uid, "count")
    assert loaded == 9 and isinstance(loaded, int)


async def test_save_returns_the_value():
    uid = uuid4()
    assert await UserStore.save(uid, "k", 7) == 7


async def test_load_missing_returns_default():
    uid = uuid4()
    assert await UserStore.load(uid, "missing") is None
    assert await UserStore.load(uid, "missing", "fallback") == "fallback"


async def test_falsy_value_not_confused_with_missing():
    uid = uuid4()
    await UserStore.save(uid, "k", 0)
    assert await UserStore.load(uid, "k", 999) == 0


async def test_overwrite_is_full_replacement():
    uid = uuid4()
    await UserStore.save(uid, "k", {"a": 1})
    await UserStore.save(uid, "k", {"b": 2})
    assert await UserStore.load(uid, "k") == {"b": 2}


async def test_delete_and_exists():
    uid = uuid4()
    assert await UserStore.exists(uid, "k") is False
    await UserStore.save(uid, "k", "v")
    assert await UserStore.exists(uid, "k") is True
    assert await UserStore.delete(uid, "k") is True
    assert await UserStore.delete(uid, "k") is False
    assert await UserStore.exists(uid, "k") is False


async def test_users_are_isolated():
    """Same key, two users, no collision."""
    alice, bob = uuid4(), uuid4()
    await UserStore.save(alice, "theme", "dark")
    await UserStore.save(bob, "theme", "light")
    assert await UserStore.load(alice, "theme") == "dark"
    assert await UserStore.load(bob, "theme") == "light"


async def test_delete_is_scoped_to_one_user():
    alice, bob = uuid4(), uuid4()
    await UserStore.save(alice, "k", 1)
    await UserStore.save(bob, "k", 2)
    await UserStore.delete(alice, "k")
    assert await UserStore.load(alice, "k") is None
    assert await UserStore.load(bob, "k") == 2  # bob untouched


async def test_user_and_global_stores_do_not_collide():
    """Same key string in the global store and a user store are different rows."""
    uid = uuid4()
    await store.save("shared", "global")
    await UserStore.save(uid, "shared", "per-user")
    assert await store.load("shared") == "global"
    assert await UserStore.load(uid, "shared") == "per-user"


# --- ambient `user` proxy --------------------------------------------------

async def test_proxy_roundtrip_inside_request_context():
    """`await user.save/load/delete` resolves to the current request's user."""
    with use_ctx(Ctx(user=_user("alice"))):
        await user.save("todos", [{"text": "buy milk", "done": False}])
        assert await user.load("todos") == [{"text": "buy milk", "done": False}]
        assert await user.load("missing", []) == []
        assert await user.delete("todos") is True
        assert await user.load("todos") is None


async def test_proxy_scopes_to_current_user():
    """Two users in two contexts never see each other's data through the proxy."""
    with use_ctx(Ctx(user=_user("alice"))):
        await user.save("secret", "alice-only")
    with use_ctx(Ctx(user=_user("bob"))):
        assert await user.load("secret") is None  # bob can't see alice's key
        await user.save("secret", "bob-only")
    with use_ctx(Ctx(user=_user("alice"))):
        assert await user.load("secret") == "alice-only"  # unchanged


async def test_proxy_preserves_scalar_type():
    with use_ctx(Ctx(user=_user("alice"))):
        await user.save("count", 9)
        loaded = await user.load("count")
        assert loaded == 9 and isinstance(loaded, int)


async def test_proxy_and_userstore_share_storage():
    """A value written via the proxy is readable via UserStore for the same id,
    proving the proxy is just sugar over UserStore."""
    alice = _user("alice")
    with use_ctx(Ctx(user=alice)):
        await user.save("k", {"v": 1})
    assert await UserStore.load(alice.id, "k") == {"v": 1}
