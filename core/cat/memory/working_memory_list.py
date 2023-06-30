from cat.memory.working_memory import WorkingMemory


class WorkingMemoryList(dict):
    """Cat's volatile memory.

    Handy class that behaves like a `dict` to store temporary custom data.

    Returns
    -------
    dict[str, list]
        Default instance is a dictionary with `history` key set to an empty list.

    Notes
    -----
    The constructor instantiates a dictionary with a `history` key set to an empty list that is further used to store
    the conversation turns between the Human and the AI.
    """

    def __init__(self):
        super().__init__(user=WorkingMemory())

    def get_working_memory(self, user_id='user'):
        self[user_id] = self.get(user_id, WorkingMemory())
        return self[user_id]
