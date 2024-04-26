
import time
from typing import List
from cat.utils import BaseModelDict
from cat.convo.messages import UserMessage
from cat.experimental.form import CatForm


class WorkingMemory(BaseModelDict):
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

    # stores conversation history
    history: List = []
    user_message_json : None | UserMessage = None
    active_form: None | CatForm = None

    # recalled memories attributes
    recall_query: str = ""
    episodic_memories: List = []
    declarative_memories: List = []
    procedural_memories: List = []

    def update_conversation_history(self, who, message, why={}):
        """Update the conversation history.

        The methods append to the history key the last three conversation turns.

        Parameters
        ----------
        who : str
            Who said the message. Can either be `Human` or `AI`.
        message : str
            The message said.
        
        """
        # append latest message in conversation
        self.history.append({"who": who, "message": message, "why": why, "when": time.time()})


