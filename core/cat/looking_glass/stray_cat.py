
from cat.mad_hatter.mad_hatter import MadHatter

# The Cheshire Cat goes around tools and hook, making troubles
class StrayCat:
    """User/session based object containing working memory and a few utility pointers"""

    def __init__(
            self,
            user_id="user",
            working_memory=None,
            llm=None,
            _llm=None,
            embedder=None
        ):
        
        self.user_id = user_id
        self.working_memory = working_memory
        self.llm = llm
        self._llm = _llm
        self.embedder = embedder
        #self.vector_memory = VectorMemory() # REFACTOR should be instantiated here
        #self.vector_memory = RabbitHole() # REFACTOR should be instantiated here
        self.mad_hatter = MadHatter()

    def send_ws_message(self, *args, **kwargs):
        """Proxy method for WorkingMemory.send_ws_message
        """
        self.working_memory.send_ws_message(*args, **kwargs)