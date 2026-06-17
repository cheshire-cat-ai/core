"""Simple key-value database abstraction for global settings."""

from typing import Any
from uuid import UUID

from cat.db.models import KeyValueDB, UserKeyValueDB


class DB:
    """
    Simple key-value database for global settings.
    Abstracts away Piccolo queries.

    Example:
        await DB.save("my_key", {"foo": "bar"})
        data = await DB.load("my_key")  # returns {"foo": "bar"} or None
    """

    @staticmethod
    async def save(key: str, value: Any) -> Any:
        """
        Save a value to the database (full replacement).

        Parameters
        ----------
        key : str
            The database key.
        value : Any
            Any JSON-serializable value.

        Returns
        -------
        Any
            The saved value.
        """
        try:
            # Try to update existing
            db_entry = await KeyValueDB.objects().where(
                KeyValueDB.key == key
            ).first().output(load_json=True)
            db_entry.value = value
            await db_entry.save()
            return db_entry.value
        except Exception:
            # Create new record
            new_entry = KeyValueDB(key=key, value=value)
            await new_entry.save()
            return value

    @staticmethod
    async def load(key: str, default: Any = None) -> Any:
        """
        Load a value from the database.

        Parameters
        ----------
        key : str
            The database key.
        default : Any
            Value to return if key not found.

        Returns
        -------
        Any
            The loaded value, or default if not found.
        """
        try:
            db_entry = await KeyValueDB.objects().where(
                KeyValueDB.key == key
            ).first().output(load_json=True)

            if db_entry is None:
                return default

            return db_entry.value
        except Exception:
            return default

    @staticmethod
    async def delete(key: str) -> bool:
        """
        Delete a key from the database.

        Parameters
        ----------
        key : str
            The database key.

        Returns
        -------
        bool
            True if deleted, False if not found.
        """
        try:
            db_entry = await KeyValueDB.objects().where(
                KeyValueDB.key == key
            ).first()

            if db_entry is None:
                return False

            await db_entry.remove()
            return True
        except Exception:
            return False

    @staticmethod
    async def exists(key: str) -> bool:
        """
        Check if a key exists in the database.

        Parameters
        ----------
        key : str
            The database key.

        Returns
        -------
        bool
            True if exists, False otherwise.
        """
        try:
            db_entry = await KeyValueDB.objects().where(
                KeyValueDB.key == key
            ).first()
            return db_entry is not None
        except Exception:
            return False


class UserDB:
    """
    Simple key-value database for user-scoped settings.
    Abstracts away Piccolo queries on UserKeyValueDB.

    Example:
        await UserDB.save(user_id, "theme", "dark")
        theme = await UserDB.load(user_id, "theme")  # returns "dark" or None
    """

    @staticmethod
    async def save(user_id: UUID, key: str, value: Any) -> Any:
        """
        Save a user-specific value to the database (full replacement).

        Parameters
        ----------
        user_id : UUID
            The user ID.
        key : str
            The database key.
        value : Any
            Any JSON-serializable value.

        Returns
        -------
        Any
            The saved value.
        """
        try:
            # Try to update existing
            db_entry = await UserKeyValueDB.objects().where(
                (UserKeyValueDB.user_id == user_id) & (UserKeyValueDB.key == key)
            ).first().output(load_json=True)

            if db_entry is None:
                # Create new record
                new_entry = UserKeyValueDB(user_id=user_id, key=key, value=value)
                await new_entry.save()
                return value
            else:
                db_entry.value = value
                await db_entry.save()
                return db_entry.value
        except Exception:
            # Create new record
            new_entry = UserKeyValueDB(user_id=user_id, key=key, value=value)
            await new_entry.save()
            return value

    @staticmethod
    async def load(user_id: UUID, key: str, default: Any = None) -> Any:
        """
        Load a user-specific value from the database.

        Parameters
        ----------
        user_id : UUID
            The user ID.
        key : str
            The database key.
        default : Any
            Value to return if key not found.

        Returns
        -------
        Any
            The loaded value, or default if not found.
        """
        try:
            db_entry = await UserKeyValueDB.objects().where(
                (UserKeyValueDB.user_id == user_id) & (UserKeyValueDB.key == key)
            ).first().output(load_json=True)

            if db_entry is None:
                return default

            return db_entry.value
        except Exception:
            return default

    @staticmethod
    async def delete(user_id: UUID, key: str) -> bool:
        """
        Delete a user-specific key from the database.

        Parameters
        ----------
        user_id : UUID
            The user ID.
        key : str
            The database key.

        Returns
        -------
        bool
            True if deleted, False if not found.
        """
        try:
            db_entry = await UserKeyValueDB.objects().where(
                (UserKeyValueDB.user_id == user_id) & (UserKeyValueDB.key == key)
            ).first()

            if db_entry is None:
                return False

            await db_entry.remove()
            return True
        except Exception:
            return False

    @staticmethod
    async def exists(user_id: UUID, key: str) -> bool:
        """
        Check if a user-specific key exists in the database.

        Parameters
        ----------
        user_id : UUID
            The user ID.
        key : str
            The database key.

        Returns
        -------
        bool
            True if exists, False otherwise.
        """
        try:
            db_entry = await UserKeyValueDB.objects().where(
                (UserKeyValueDB.user_id == user_id) & (UserKeyValueDB.key == key)
            ).first()
            return db_entry is not None
        except Exception:
            return False
