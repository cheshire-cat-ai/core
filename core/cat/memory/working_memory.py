from typing import List, Optional
from langchain_core.messages import BaseMessage

from cat.convo.messages import Role, ConversationMessage, UserMessage, CatMessage
from cat.convo.model_interactions import ModelInteraction
from cat.experimental.form import CatForm
from cat.utils import BaseModelDict, deprecation_warning


class WorkingMemory(BaseModelDict):
    """
    Represents the volatile memory of a cat, functioning similarly to a dictionary to store temporary custom data.

    Attributes
    ----------
    history : List[HistoryMessage]
        A list that maintains the conversation history between the Human and the AI.
    user_message_json : Optional[UserMessage], default=None
        An optional UserMessage object representing the last user message.
    active_form : Optional[CatForm], default=None
        An optional reference to a CatForm currently in use.
    recall_query : str, default=""
        A string that stores the last recall query.
    episodic_memories : List
        A list for storing episodic memories.
    declarative_memories : List
        A list for storing declarative memories.
    procedural_memories : List
        A list for storing procedural memories.
    model_interactions : List[ModelInteraction]
        A list of interactions with models.
    """

    history: List[ConversationMessage] = []

    user_message_json: Optional[UserMessage] = None

    active_form: Optional[CatForm] = None
    recall_query: str = ""
    
    episodic_memories: List = []
    declarative_memories: List = []
    procedural_memories: List = []
    
    model_interactions: List[ModelInteraction] = []

    def update_conversation_history(self, message: str, who: str, why = {}):
        """
        This method is deprecated. Use `update_history` instead.
        
        Updates the conversation history with the most recent message.

        Parameters
        ----------
        message :str
            The text content of the message.
        who : str
            The name of the message author.
        why : Optional[Dict[str, Any]], default=None
            Optional explanation for the message.

        Notes
        -----
        This method is deprecated and will be removed in future versions. Use `update_history` instead.
        """
         
        deprecation_warning(
            "update_conversation_history is deprecated and will be removed in a future release. Use update_history instead."
        )
        role = Role.AI if who == "AI" else Role.Human

        if role == Role.AI:
            content = CatMessage(
                user_id=self.user_message_json.user_id,
                who=who,
                text=message,
                why=why,
            )
        else:
            content = UserMessage(
                user_id=self.user_message_json.user_id,
                who=who,
                text=message
            )

        self.history.append(content)

    def update_history(self, message: ConversationMessage):
        """
        Adds a message to the history.

        Parameters
        ----------
        message : ConversationMessage
            The message, must be of type `ConversationMessage` (typically a subclass like `UserMessage` or `CatMessage`).
        """
        self.history.append(message)
      

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

        history = self.history[-latest_n:]

        history_string = ""
        for turn in history:
            history_string += f"\n - {turn.who}: {turn.text}"

        return history_string

    def langchainfy_chat_history(self, latest_n: int = 5) -> List[BaseMessage]: 
        
        chat_history = self.history[-latest_n:]
        recent_history = chat_history[-latest_n:]
        langchain_chat_history = []

        for message in recent_history:
            langchain_chat_history.append(
                message.langchainfy()    
            )

        return langchain_chat_history
