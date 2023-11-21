import asyncio
from typing import get_args, Literal

from cat.mad_hatter.mad_hatter import MadHatter

MSG_TYPES = Literal["notification", "chat", "error", "chat_token"]

# The Cheshire Cat goes around tools and hook, making troubles
class StrayCat:
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

        # event loop and ws messages queue
        self._loop = asyncio.get_event_loop()
        self.ws_messages = asyncio.Queue()

    def send_ws_message(self, content: str, msg_type: MSG_TYPES = "notification"):
        """Send a message via websocket.

        This method is useful for sending a message via websocket directly without passing through the LLM

        Parameters
        ----------
        content : str
            The content of the message.
        msg_type : str
            The type of the message. Should be either `notification`, `chat`, `chat_token` or `error`
        """

        options = get_args(MSG_TYPES)

        if msg_type not in options:
            raise ValueError(f"The message type `{msg_type}` is not valid. Valid types: {', '.join(options)}")

        if msg_type == "error":
            self._loop.create_task(
                self.ws_messages.put(
                    {
                        "type": msg_type,
                        "name": "GenericError",
                        "description": content
                    }
                )
            )
        else:
            self._loop.create_task(
                self.ws_messages.put(
                    {
                        "type": msg_type,
                        "content": content
                    }
                )
            )