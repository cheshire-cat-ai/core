"""Key-value store helpers backing the ambient `store` and `user` APIs.

Values are persisted as JSON text and decoded back on read, so any
JSON-serializable value round-trips with its type intact — numbers stay
numbers, strings stay strings, not just dicts:

    await store.save("count", 9)
    await store.load("count")        # 9  (int, not "9")

The two JSON-type coercions are the usual ones: tuples come back as lists,
and non-string dict keys come back as strings.
"""

import json
from typing import Any
from uuid import UUID

from cat.db.models import KeyValueDB, UserKeyValueDB


def _encode(value: Any) -> str:
    """Serialize any JSON-serializable value to the text stored in the column.

    We encode explicitly rather than relying on the Piccolo `JSON` column's
    own serialization, which only encodes dicts/lists and stores bare scalars
    (ints, floats, strings) raw — making them undecodable on read.
    """
    return json.dumps(value)


def _decode(raw: Any) -> Any:
    """Decode a value read back from the column.

    `raw` is normally the JSON text we stored, but stay robust to a column
    that hands back an already-decoded value: only parse actual JSON text.
    """
    if isinstance(raw, (str, bytes, bytearray)):
        return json.loads(raw)
    return raw


class Store:
    """
    The global (installation-wide) key-value store.

    Same four verbs as the per-user `user` proxy, but shared across all users.
    Exposed to plugins as the ambient `store`:

        from cat import store
        await store.save("theme", {"color": "dark"})
        theme = await store.load("theme")   # {"color": "dark"} or None

    Abstracts away Piccolo queries on the `ccat_global_key_value` table.
    """

    @staticmethod
    async def save(key: str, value: Any) -> Any:
        """
        Save a value (full replacement) and return it.

        Parameters
        ----------
        key : str
            The database key.
        value : Any
            Any JSON-serializable value.

        Returns
        -------
        Any
            The saved value (the same object you passed in).
        """
        payload = _encode(value)
        db_entry = await KeyValueDB.objects().where(KeyValueDB.key == key).first()
        if db_entry is None:
            await KeyValueDB(key=key, value=payload).save()
        else:
            db_entry.value = payload
            await db_entry.save()
        return value

    @staticmethod
    async def load(key: str, default: Any = None) -> Any:
        """
        Load a value, or return `default` if the key is unset.

        Parameters
        ----------
        key : str
            The database key.
        default : Any
            Value to return if the key is not found.

        Returns
        -------
        Any
            The stored value (with its original type), or `default`.
        """
        db_entry = await KeyValueDB.objects().where(KeyValueDB.key == key).first()
        if db_entry is None:
            return default
        return _decode(db_entry.value)

    @staticmethod
    async def delete(key: str) -> bool:
        """
        Delete a key.

        Returns
        -------
        bool
            True if a value was removed, False if the key was unset.
        """
        db_entry = await KeyValueDB.objects().where(KeyValueDB.key == key).first()
        if db_entry is None:
            return False
        await db_entry.remove()
        return True

    @staticmethod
    async def exists(key: str) -> bool:
        """
        Check whether a key is set.

        Returns
        -------
        bool
            True if the key exists, False otherwise.
        """
        db_entry = await KeyValueDB.objects().where(KeyValueDB.key == key).first()
        return db_entry is not None


class UserStore:
    """
    The per-user key-value store. Same shape as `Store`, but every row is
    scoped to a `user_id` so two users never collide.

    Backs the `user.save/load/delete` ambient API (see `cat.auth.user.User`).
    Abstracts away Piccolo queries on the `ccat_user_key_value` table.

    Example:
        await UserStore.save(user_id, "theme", "dark")
        theme = await UserStore.load(user_id, "theme")  # "dark" or None
    """

    @staticmethod
    async def save(user_id: UUID, key: str, value: Any) -> Any:
        """
        Save a user-scoped value (full replacement) and return it.

        Parameters
        ----------
        user_id : UUID
            The user the value belongs to.
        key : str
            The database key.
        value : Any
            Any JSON-serializable value.

        Returns
        -------
        Any
            The saved value (the same object you passed in).
        """
        payload = _encode(value)
        db_entry = await UserKeyValueDB.objects().where(
            (UserKeyValueDB.user_id == user_id) & (UserKeyValueDB.key == key)
        ).first()
        if db_entry is None:
            await UserKeyValueDB(user_id=user_id, key=key, value=payload).save()
        else:
            db_entry.value = payload
            await db_entry.save()
        return value

    @staticmethod
    async def load(user_id: UUID, key: str, default: Any = None) -> Any:
        """
        Load a user-scoped value, or return `default` if the key is unset.

        Parameters
        ----------
        user_id : UUID
            The user the value belongs to.
        key : str
            The database key.
        default : Any
            Value to return if the key is not found.

        Returns
        -------
        Any
            The stored value (with its original type), or `default`.
        """
        db_entry = await UserKeyValueDB.objects().where(
            (UserKeyValueDB.user_id == user_id) & (UserKeyValueDB.key == key)
        ).first()
        if db_entry is None:
            return default
        return _decode(db_entry.value)

    @staticmethod
    async def delete(user_id: UUID, key: str) -> bool:
        """
        Delete a user-scoped key.

        Returns
        -------
        bool
            True if a value was removed, False if the key was unset.
        """
        db_entry = await UserKeyValueDB.objects().where(
            (UserKeyValueDB.user_id == user_id) & (UserKeyValueDB.key == key)
        ).first()
        if db_entry is None:
            return False
        await db_entry.remove()
        return True

    @staticmethod
    async def exists(user_id: UUID, key: str) -> bool:
        """
        Check whether a user-scoped key is set.

        Returns
        -------
        bool
            True if the key exists, False otherwise.
        """
        db_entry = await UserKeyValueDB.objects().where(
            (UserKeyValueDB.user_id == user_id) & (UserKeyValueDB.key == key)
        ).first()
        return db_entry is not None
