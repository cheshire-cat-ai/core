from cat.db.helper import Store, UserStore
from cat.db.models import KeyValueDB, UserKeyValueDB, UserScopedDB

# Ambient global key-value store. `Store` is just static methods (no request
# context), so the lowercase ambient name is the class itself — no proxy needed,
# unlike `user`.
store = Store

__all__ = [
    "store",
    "Store",
    "UserStore",
    "KeyValueDB",
    "UserKeyValueDB",
    "UserScopedDB",
]
