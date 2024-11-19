import time
from typing import List
from cat.utils import BaseModelDict
from cat.convo.messages import Role, UserMessage, ModelInteraction
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
    user_message_json: None | UserMessage = None
    active_form: None | CatForm = None

    # recalled memories attributes
    recall_query: str = ""
    episodic_memories: List = []
    declarative_memories: List = []
    procedural_memories: List = []

    # track models usage
    model_interactions: List[ModelInteraction] = []
    
    def stringify_chat_history(self, latest_n: int = 5) -> str:
        """Serialize chat history.
        Converts to text the recent conversation turns.

        Parameters
        ----------
        latest_n : int
            Hoe many latest turns to stringify.

        Returns
        -------
        history : str
            String with recent conversation turns.

        Notes
        -----
        Such context is placed in the `agent_prompt_suffix` in the place held by {chat_history}.

        The chat history is a dictionary with keys::
            'who': the name of who said the utterance;
            'message': the utterance.

        """

        history = self.working_memory.history[-latest_n:]

        history_string = ""
        for turn in history:
            history_string += f"\n - {turn['who']}: {turn['message']}"

        return history_string

    def langchainfy_chat_history(self, latest_n: int = 5) -> List[BaseMessage]:
        chat_history = self.working_memory.history[-latest_n:]

        langchain_chat_history = []
        for message in chat_history:
            if message["role"] == Role.Human:
                langchain_chat_history.append(
                    HumanMessage(name=message["who"], content=message["message"])
                )
            else:
                langchain_chat_history.append(
                    AIMessage(name=message["who"], content=message["message"])
                )

        return langchain_chat_history


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
        # TODO: Message should be of type CatMessage or UserMessage. For retrocompatibility we put a new key
        # we are sure that who is not change in the current call
        self.history.append(
            {
                "who": who,
                "message": message,
                "why": why,
                "when": time.time(),
                "role": Role.AI if who == "AI" else Role.Human,
            }
        )
