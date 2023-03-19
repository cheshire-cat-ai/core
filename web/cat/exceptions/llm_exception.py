class NoModelKeyProvided(Exception):
    def __init__(self, message="No model key was provided!"):
        self.message = message
        super().__init__(self.message)
