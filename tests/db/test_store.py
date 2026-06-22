"""
The global key-value store (`from cat import store`).

The autouse `isolated_project` fixture (in `cat.testing`) scaffolds a fresh
SQLite project with empty tables for every test, so these talk to a real DB —
no mocking of the persistence layer.
"""

import pytest

from cat.db import store


# Every JSON type, including the bare scalars that the old implementation
# silently dropped. Each case asserts both value AND Python type survive.
ROUNDTRIP_CASES = [
    ("int", 9),
    ("zero", 0),
    ("negative_int", -42),
    ("float", 3.14),
    ("str", "hello"),
    ("empty_str", ""),
    ("unicode", "héllo 🐱 世界"),
    ("bool_true", True),
    ("bool_false", False),
    ("none", None),
    ("list", [1, 2, 3]),
    ("empty_list", []),
    ("dict", {"a": 1, "b": "two"}),
    ("empty_dict", {}),
    ("nested", {"users": [{"id": 1, "tags": ["x", "y"]}], "n": 2, "ok": True}),
]


@pytest.mark.parametrize("name,value", ROUNDTRIP_CASES, ids=[c[0] for c in ROUNDTRIP_CASES])
async def test_roundtrip_preserves_value_and_type(name, value):
    await store.save(name, value)
    loaded = await store.load(name)
    assert loaded == value
    # bool is an int subclass — `type(...) is` keeps True/1 and False/0 distinct.
    assert type(loaded) is type(value)


async def test_number_comes_back_as_number_not_string():
    """The headline bug: a saved int must load as an int, not '9'."""
    await store.save("count", 9)
    loaded = await store.load("count")
    assert loaded == 9
    assert isinstance(loaded, int)
    assert not isinstance(loaded, str)


async def test_save_returns_the_value():
    assert await store.save("k", {"x": 1}) == {"x": 1}
    assert await store.save("n", 7) == 7


async def test_load_missing_returns_none_by_default():
    assert await store.load("never_set") is None


async def test_load_missing_returns_custom_default():
    assert await store.load("never_set", "fallback") == "fallback"
    assert await store.load("never_set", []) == []


async def test_default_is_ignored_when_key_exists():
    await store.save("k", 0)
    # 0 is falsy — a naive `value or default` would wrongly return the default.
    assert await store.load("k", 999) == 0


async def test_empty_container_is_not_confused_with_missing():
    await store.save("empty", [])
    assert await store.load("empty", ["default"]) == []


async def test_overwrite_is_full_replacement():
    await store.save("k", {"a": 1, "b": 2})
    await store.save("k", {"c": 3})
    assert await store.load("k") == {"c": 3}


async def test_overwrite_can_change_type():
    await store.save("k", 9)
    await store.save("k", "nine")
    loaded = await store.load("k")
    assert loaded == "nine"
    assert isinstance(loaded, str)


async def test_keys_are_independent():
    await store.save("a", 1)
    await store.save("b", 2)
    assert await store.load("a") == 1
    assert await store.load("b") == 2


async def test_delete_removes_value():
    await store.save("k", "v")
    assert await store.delete("k") is True
    assert await store.load("k") is None
    assert await store.exists("k") is False


async def test_delete_missing_returns_false():
    assert await store.delete("never_set") is False


async def test_exists_reflects_presence():
    assert await store.exists("k") is False
    await store.save("k", "v")
    assert await store.exists("k") is True


async def test_exists_true_even_for_falsy_and_none_values():
    """`exists` distinguishes a stored `None`/falsy value from a missing key,
    which `load` alone cannot."""
    await store.save("none_val", None)
    await store.save("false_val", False)
    assert await store.exists("none_val") is True
    assert await store.exists("false_val") is True
    # load returns None for both a stored None and a missing key — exists is
    # the only way to tell them apart.
    assert await store.load("none_val") is None


async def test_whole_number_float_may_come_back_as_int():
    """Documented SQLite limitation: the JSON column has NUMERIC affinity, so a
    whole-number float like 9.0 is stored as integer 9. Value equality still
    holds (9.0 == 9); only the Python type narrows. Fractional floats (3.14)
    are unaffected and keep their type (covered by the roundtrip matrix)."""
    await store.save("k", 9.0)
    loaded = await store.load("k")
    assert loaded == 9.0  # equality preserved
    assert isinstance(loaded, int)  # type narrowed by SQLite affinity


async def test_tuple_is_coerced_to_list():
    """Documented JSON coercion — tuples are not a JSON type."""
    await store.save("k", (1, 2, 3))
    loaded = await store.load("k")
    assert loaded == [1, 2, 3]
    assert isinstance(loaded, list)


async def test_re_save_after_delete():
    await store.save("k", 1)
    await store.delete("k")
    await store.save("k", 2)
    assert await store.load("k") == 2
