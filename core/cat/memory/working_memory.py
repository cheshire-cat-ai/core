from typing import List, Optional
from langchain_core.messages import BaseMessage

from cat.convo.messages import Role, ConversationMessage, UserMessage, CatMessage
from cat.convo.model_interactions import ModelInteraction
from cat.experimental.form import CatForm
from cat.utils import BaseModelDict, deprecation_warning

MAX_WORKING_HISTORY_LENGTH = 20

class WorkingMemory(BaseModelDict):
    """
    Represents the volatile memory of a cat, functioning similarly to a dictionary to store temporary custom data.

    Attributes
    ----------
    history : List[ConversationMessage]
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
        self.history = self.history[-MAX_WORKING_HISTORY_LENGTH:]


    def stringify_chat_history(self, latest_n: int = MAX_WORKING_HISTORY_LENGTH) -> str:
        """Serialize chat history.
        Converts to text the recent conversation turns.
        Useful for retrocompatibility with old non-chat models, and to easily insert convo into a prompt without using dedicated objects and libraries.

        Parameters
        ----------
        latest_n : int
            How many latest turns to stringify.

        Returns
        -------
        history : str
            String with recent conversation turns.
        """

        history = self.history[-latest_n:]

        history_string = ""
        for turn in history:
            history_string += f"\n - {turn.who}: {turn.text}"

        return history_string

    def langchainfy_chat_history(self, latest_n: int = MAX_WORKING_HISTORY_LENGTH) -> List[BaseMessage]: 
        """Convert chat history in working memory to langchain objects.

        Parameters
        ----------
        latest_n : int
            How many latest turns to convert.

        Returns
        -------
        history : List[BaseMessage]
            List of langchain HumanMessage / AIMessage.
        """
        
        recent_history = self.history[-latest_n:]
        langchain_chat_history = []

        for message in recent_history:
            langchain_chat_history.append(
                message.langchainfy()    
            )

        return langchain_chat_history
