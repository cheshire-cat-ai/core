import os
import pickle
from cat.cache.base_cache import BaseCache


class FileSystemCache(BaseCache):
    """Cache implementation using the file system.

    Attributes
    ----------
    cache_dir : str
        Directory to store the cache.

    """

    def __init__(self, cache_dir):
        self.cache_dir = cache_dir
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def _get_file_path(self, key):
        return os.path.join(self.cache_dir, f"{key}.cache")

    def insert(self, cache_item):
        """Insert a key-value pair in the cache.

        Parameters
        ----------
        cache_item : CacheItem
            Cache item to store.

        """

        with open(self._get_file_path(cache_item.key), "wb") as f:
            pickle.dump(cache_item, f)

    def get_item(self, key):
        """Get the value stored in the cache.

        Parameters
        ----------
        key : str
            Key to retrieve the value.

        Returns
        -------
        any
            Value stored in the cache.

        """
        file_path = self._get_file_path(key)
        if not os.path.exists(file_path):
            return None

        with open(file_path, "rb") as f:
            cache_item = pickle.load(f)

        if cache_item.is_expired():
            os.remove(file_path)
            return None

        return cache_item

    def get_value(self, key):
        """Get the value stored in the cache.

        Parameters
        ----------
        key : str
            Key to retrieve the value.

        Returns
        -------
        any
            Value stored in the cache.

        """

        cache_item = self.get_item(key)
        if cache_item:
            return cache_item.value
        return None

    def delete(self, key):
        """Delete a key-value pair from the cache.

        Parameters
        ----------
        key : str
            Key to delete the value.

        """
        file_path = self._get_file_path(key)
        if os.path.exists(file_path):
            os.remove(file_path)


