import time
import base64
from io import BytesIO
from enum import Enum
from typing import List, Optional
import requests
from PIL import Image

from pydantic import Field, computed_field
from langchain_core.messages import AIMessage, HumanMessage

from cat.convo.model_interactions import LLMModelInteraction, EmbedderModelInteraction
from cat.utils import BaseModelDict, deprecation_warning
from cat.log import log


class Role(Enum):
    """
    Enum representing the roles involved in a conversation.

    Attributes
    ----------
    AI : str
        Represents an artificial intelligence role.
    Human : str
        Represents a human role.
    """

    AI = "AI"
    Human = "Human"


class MessageWhy(BaseModelDict):
    """
    A class for encapsulating the context and reasoning behind a message, providing details on 
    input, intermediate steps, memory, and interactions with models.

    Attributes
    ----------
    input : str
        The initial input message that triggered the response.
    intermediate_steps : List
        A list capturing intermediate steps or actions taken as part of processing the message.
    memory : dict
        A dictionary containing relevant memory information used during the processing of the message.
    model_interactions : List[Union[LLMModelInteraction, EmbedderModelInteraction]]
        A list of interactions with language or embedding models, detailing how models were used in generating 
        or understanding the message context.
    """

    input: str
    intermediate_steps: List
    memory: dict
    model_interactions: List[LLMModelInteraction | EmbedderModelInteraction]


class Message(BaseModelDict):
    """
    Base class for working memory history entries.
    Is subclassed by `ConversationMessage`, which in turns is subclassed by `CatMessage` and `UserMessage`.
    
    Attributes
    ----------
    user_id : str
        Unique identifier for the user associated with the message.
    when : float
        The timestamp when the message was sent.
    """

    user_id: str   
    when: float = Field(default_factory=time.time)


class ConversationMessage(Message):
    """
    Base class for conversation messages, containing common attributes shared by all message types.
    Subclassed by `CatMessage` and `UserMessage`.

    Attributes
    ----------
    user_id : str
        Unique identifier for the user associated with the message.
    when : float
        The timestamp when the message was sent. Defaults to the current time.
    who : str
        The name of the message author.
    text : Optional[str], default=None
        The text content of the message.
    image : Optional[str], default=None
        Image file URLs or base64 data URIs that represent image associated with the message.
    audio : Optional[str], default=None
        Audio file URLs or base64 data URIs that represent audio associated with the message.
    """

    who: str
    text: Optional[str]  = None
    image: Optional[str] = None
    audio: Optional[str] = None

    # massage was used in the old history instead of text
    # we need to keep it for backward compatibility
    def __init__(self, **data):

        if "message" in data:
            deprecation_warning("The `message` parameter is deprecated. Use `text` instead.")
            data["text"] = data.pop("message")

        super().__init__(**data)

    @property
    def message(self) -> str:
        """
        This attribute is deprecated. Use `text` instead.

        The text content of the message. Use `text` instead.

        Returns
        -------
        str
            The text content of the message.
        """
        deprecation_warning("The `message` attribute is deprecated. Use `text` instead.")
        return self.text
    
    @message.setter
    def message(self, value):
        deprecation_warning("The `message` attribute is deprecated. Use `text` instead.")
        self.text = value

    @property
    def role(self) -> None:
        """The role of the message author."""
        return None


class CatMessage(ConversationMessage):
    """
    Represents a Cat message.

    Attributes
    ----------
    type : str
        The type of message. Defaults to "chat".
    user_id : str
        Unique identifier for the user associated with the message.
    when : float
        The timestamp when the message was sent. Defaults to the current time.
    who : str
        The name of the message author.
    text : Optional[str], default=None
        The text content of the message.
    image : Optional[str], default=None
        Image file URLs or base64 data URIs that represent image associated with the message.
    audio : Optional[str], default=None
        Audio file URLs or base64 data URIs that represent audio associated with the message.
    why : Optional[MessageWhy]
        Additional contextual information related to the message.

    Notes
    -----
    - The `content` parameter and attribute are deprecated. Use `text` instead.
    """

    who: str = "AI"
    type: str = "chat" # For now is always "chat" and is not used
    why: Optional[MessageWhy] = None

    def __init__(
        self,
        user_id: str,
        who: str = "AI",
        text: Optional[str] = None,
        image: Optional[str] = None,
        audio: Optional[str] = None,
        why: Optional[MessageWhy] = None,
        **kwargs,
    ):
        if "content" in kwargs:
            deprecation_warning("The `content` parameter is deprecated. Use `text` instead.")    
            text = kwargs.pop("content")  # Map 'content' to 'text'

        super().__init__(user_id=user_id, text=text, image=image, audio=audio, why=why, who=who, **kwargs)

    @computed_field
    @property
    def content(self) -> str:
        """
        This attribute is deprecated. Use `text` instead.

        The text content of the message. Use `text` instead.

        Returns
        -------
        str
            The text content of the message.
        """
        return self.text
    
    @content.setter
    def content(self, value):
        deprecation_warning("The `content` attribute is deprecated. Use `text` instead.", skip=4)
        self.text = value

    @property
    def role(self) -> Role:
        """The role of the message author."""
        return Role.AI
    
    def langchainfy(self) -> AIMessage:
        """
        Convert the internal CatMessage to a LangChain AIMessage.

        Returns
        -------
        AIMessage
            The LangChain AIMessage converted from the internal CatMessage.
        """

        return AIMessage(
            name=self.who,
            content=self.text
        )


class UserMessage(ConversationMessage):
    """
    Represents a message from a user, containing text and optional multimedia content such as image and audio.

    This class is used to encapsulate the details of a message sent by a user, including the user's identifier, 
    the text content of the message, and any associated multimedia content such as image or audio files.

    Attributes
    ----------
    user_id : str
        Unique identifier for the user associated with the message.
    when : float
        The timestamp when the message was sent. Defaults to the current time.
    who : str
        The name of the message author.
    text : Optional[str], default=None
        The text content of the message.
    image : Optional[str], default=None
        Image file URLs or base64 data URIs that represent image associated with the message.
    audio : Optional[str], default=None
        Audio file URLs or base64 data URIs that represent audio associated with the message.
    """

    who: str = "Human"

    @property
    def role(self) -> Role:
        """The role of the message author."""
        return Role.Human

    def langchainfy(self) -> HumanMessage:
        """
        Convert the internal UserMessage to a LangChain HumanMessage.

        Returns
        -------
        HumanMessage
            The LangChain HumanMessage converted from the internal UserMessage.
        """

        content = []

        if self.text:
            content.append({"type": "text", "text": self.text})

        if self.image:
            formatted_image = self.langchainfy_image()
            if formatted_image:
                content.append(formatted_image)
        
        return HumanMessage(
            name=self.who,
            content=content
        )
    
    def langchainfy_image(self) -> dict:
        """
        Format an image to be sent as a data URI.

        Returns
        -------
        dict
            A dictionary containing the image data URI.
        """

        # If the image is a URL, download it and encode it as a data URI
        if self.image.startswith("http"):
            response = requests.get(self.image)
            if response.status_code == 200:
                # Open the image using Pillow to determine its MIME type
                img = Image.open(BytesIO(response.content))
                mime_type = img.format.lower()  # Get MIME type
                
                # Encode the image to base64
                encoded_image = base64.b64encode(response.content).decode('utf-8')
                image_uri = f"data:image/{mime_type};base64,{encoded_image}"
                
                # Add the image as a data URI with the correct MIME type
                return {"type": "image_url", "image_url": {"url": image_uri}}
            else:
                error_message = f"Unexpected error with status code {response.status_code}"
                if response.text:
                    error_message = response.text
                log.error(f"Failed to download image: {error_message} from {self.image}")

                return None
        
        return {"type": "image_url", "image_url": {"url": self.image}}