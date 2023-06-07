class WorkingMemory(dict):

    """Handy class that behaves like a `dict` to store custom data."""

    def __init__(self):
        # The constructor instantiates a `dict` with a 'history' key to store conversation history
        super().__init__(history=[])

    def update_conversation_history(self, who, message):
        
        # append latest message in conversation
        self["history"].append({"who": who, "message": message})

        # do not allow more than k messages in convo history (+2 which are the current turn)
        k = 3
        self["history"] = self["history"][(-k-1):]


