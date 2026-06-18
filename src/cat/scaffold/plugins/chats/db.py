from piccolo.columns import JSON

from cat.db import UserScopedDB


class ChatDB(UserScopedDB):
    """A saved conversation: its messages and the context they ran in."""

    messages = JSON()
    context = JSON()

    class Meta:
        tablename = "ccat_chats"


ChatDB.create_table(if_not_exists=True).run_sync()
