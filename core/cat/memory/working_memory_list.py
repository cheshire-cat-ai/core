from cat.memory.working_memory import WorkingMemory


class WorkingMemoryList(dict):
    """Cat's volatile memory list.

    Handy class that behaves like a `dict` to store temporary custom data.

    Returns
    -------
    dict[str, list]
        Default instance is a dictionary with `user` key set to a WorkingMemory instance.

    Notes
    -----
    The constructor instantiates a dictionary with a `user` key set to a WorkingMemory instance that is further used to
    reference the anonymous WorkingMemory.
    """

    def __init__(self):
        super().__init__(user=WorkingMemory())

    def get_working_memory(self, user_id='user'):
        self[user_id] = self.get(user_id, WorkingMemory())
        return self[user_id]
