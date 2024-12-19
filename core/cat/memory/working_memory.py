import time
from typing import List, Optional, Union

from pydantic import Field, computed_field

from cat.convo.messages import Role, UserMessage, CatMessage, MessageWhy, ModelInteraction
from cat.experimental.form import CatForm
from cat.utils import BaseModelDict, deprecation_warning


class HistoryEntry(BaseModelDict):
    """
    Represents a single entry in a conversation history, capturing the role of the speaker, the time of the message, 
    and the content of the message itself.

    Parameters
    ----------
    content : Union[UserMessage, CatMessage]
        The content of the message, which can be a UserMessage or a CatMessage.
     when : float
        The timestamp indicating when the message was created. Defaults to the current time.

    Attributes
    ----------
    role : Role
        The role of the speaker (AI or Human).
    when : float
        The timestamp of the message. Defaults to the current time.
    content : Union[UserMessage, CatMessage]
        The message content, either from a user or an AI.
    
    Notes
    -----
    - The `message`, `why`, and `who` attributes are deprecated and should be accessed through the `content` attribute instead.
    """

    when: float = Field(default_factory=time.time)
    content: Union[UserMessage, CatMessage]

    def __init__(self, content: Union[UserMessage, CatMessage], when: Optional[float] = None, **data):

        if "message" in data:
            deprecation_warning("The `message` attribute is deprecated. Use `content.text` instead.")
            content.text = data.pop("message")

        # Use the when parameter if provided otherwise the default factory provide the current time
        if when is not None:
            data["when"] = when

        super().__init__(content=content, **data)


    @computed_field
    @property
    def role(self) -> Role:
        """
        Get the role of the speaker.

        Returns
        -------
        Role
            The role of the speaker.
        """
        return Role.AI if isinstance(self.content, CatMessage) else Role.Human


    @computed_field
    @property
    def message(self) -> str:
        """
        This attribute is deprecated. Use `content.text` instead.

        Get the text content of the message.

        Returns
        -------
        str
            The text content of the message.
        """
        deprecation_warning("Accessing the `message` attribute directly is deprecated. Use `content.text` instead.")
        return self.content.text
    
    @message.setter
    def message(self, value):
        deprecation_warning("Accessing the `message` attribute directly is deprecated. Use `.text` instead.")
        self.text = value


    @computed_field
    @property
    def why(self) -> MessageWhy:
        """
        This attribute is deprecated. Use `content.why` instead.

        Deprecated. Get additional context about the message.

        Returns
        -------
        MessageWhy
            An object containing additional information related to the message.

        Notes:
            - This attribute is available only if the content is a CatMessage.
        """ 
        deprecation_warning("Accessing the `why` attribute directly is deprecated. Use `content.why` instead.")


        # NOTE: Tests expect a dictionary, not a MessageWhy object
        # if the content is a UserMessage

        # TODO: Discuss if we should return an empty dictionary or None

        if not hasattr(self.content, "why"):
            return {}
       
        return self.content.why
    
    @why.setter
    def why(self, value):
        deprecation_warning("Accessing the `why` attribute directly is deprecated. Use `content.why` instead.")        
        self.content.why = value
    

    @computed_field
    @property
    def who(self) -> str:
        """
        This attribute is deprecated. Use `content.who` instead.

        Get the name of the message author.

        Returns
        -------
        str
            The author of the speaker.

        """
        deprecation_warning("Accessing the `who` attribute directly is deprecated. Use `content.who` instead.")
        return self.content.who
      
    @who.setter
    def who(self, value):
        deprecation_warning("Accessing the `who` attribute directly is deprecated. Use `content.who` instead.")
        self.content.who = value


class WorkingMemory(BaseModelDict):
    """
    Represents the volatile memory of a cat, functioning similarly to a dictionary to store temporary custom data.

    Attributes
    ----------
    history : List[HistoryEntry]
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

    history: List[HistoryEntry] = []

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

        self.history.append(HistoryEntry(content=content))

    def update_history(self, content: Union[UserMessage, CatMessage], when: Optional[float] = None):
        """
        Adds a message to the history.

        Parameters
        ----------
        content : Union[UserMessage, CatMessage]
            The message content, must be of type `UserMessage` or `CatMessage`.
        """
        self.history.append(HistoryEntry(content=content, when=when))
      
