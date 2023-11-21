from cat.mad_hatter.mad_hatter import MadHatter

class Cat:
    """User/session based object containing working memory and a few utility pointers"""

    def __init__(
            self,
            user_id="user",
            working_memory=None,
            llm=None,
            embedder=None
        ):
        
        self.user_id = user_id
        self.working_memory = working_memory
        self.llm = llm
        self.embedder = embedder
        #self.vector_memory = VectorMemory() # REFACTOR should be instantiated here
        #self.vector_memory = RabbitHole() # REFACTOR should be instantiated here
        self.mad_hatter = MadHatter()

    def send_ws_message(self):
        # REFACTOR TODO
        pass