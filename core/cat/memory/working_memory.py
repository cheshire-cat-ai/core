class WorkingMemory(dict):

    """Handy class that behaves like a `dict` to store custom data."""

    def __init__(self):
        # The constructor instantiates a `dict` with a 'history' key to store conversation history
        super().__init__(history=[])

    def update_conversation_history(self, who, message):
        self["history"].append({"who": who, "message": message})
