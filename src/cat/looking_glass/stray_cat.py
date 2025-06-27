import time
import asyncio
import tiktoken

from typing import Literal, get_args, List, Dict, Union, Any

from websockets.exceptions import ConnectionClosedOK

from langchain.docstore.document import Document
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.runnables import RunnableConfig, RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.string import StrOutputParser

from cat.auth.permissions import AuthUserInfo
from cat.looking_glass.cheshire_cat import CheshireCat
from cat.looking_glass.callbacks import NewTokenHandler, ModelInteractionHandler
from cat.memory.working_memory import WorkingMemory
from cat.convo.messages import CatMessage, UserMessage, MessageWhy, EmbedderModelInteraction
from cat.agents import AgentOutput
from cat.cache.cache_item import CacheItem
from cat import utils
from cat.log import log

MSG_TYPES = Literal["notification", "chat", "error", "chat_token"]

# The Stray cat goes around tools, hooks and endpoints... making troubles
class StrayCat:
    """Session object containing user data, conversation state and many utility pointers.
    The framework creates an instance for every http request and websocket connection, making it available for plugins.

    You will be interacting with an instance of this class directly from within your plugins:

     - in `@hook`, `@tool` and `@endpoint` decorated functions will be passed as argument `cat` or `stray`
     - in `@form` decorated classes you can access it via `self.cat`

    Parameters
    ----------
    user_data : AuthUserInfo
        User data object containing user information.
    """

    working_memory: WorkingMemory
    """State machine containing the conversation state, acting as a simple dictionary / object.
    Can be used in plugins to store and retrieve data to drive the conversation or do anything else.

    Examples
    --------
    Store a value in the working memory during conversation
    >>> cat.working_memory["location"] = "Rome"
    or
    >>> cat.working_memory.location = "Rome"

    Retrieve a value in later conversation turns
    >>> cat.working_memory["location"]
    "Rome"
    >>> cat.working_memory.location
    "Rome"
    """

    def __init__(
        self,
        user_data: AuthUserInfo
    ):

        # user data
        self.__user_id = user_data.name # TODOV2: use id
        self.__user_data = user_data
        
        # get working memory from cache or create a new one
        self.load_working_memory_from_cache()

    def __repr__(self):
        return f"StrayCat(user_id={self.user_id}, user_name={self.user_data.name})"

    def __send_ws_json(self, data: Any):
        # Run the corutine in the main event loop in the main thread
        # and wait for the result

        app = CheshireCat().fastapi_app
        ws_manager = app.state.websocket_manager
        ws_connection = ws_manager.get_connection(self.user_id)
        if not ws_connection:
            log.debug(f"No websocket connection is open for user {self.user_id}")
            return

        asyncio.run_coroutine_threadsafe(
            ws_connection.send_json(data),
            app.state.event_loop,
        ).result()

    def __build_why(self) -> MessageWhy:
        # build data structure for output (response and why with memories)
        # TODO: these 3 lines are a mess, simplify
        episodic_report = [
            dict(d[0]) | {"score": float(d[1]), "id": d[3]}
            for d in self.working_memory.episodic_memories
        ]
        declarative_report = [
            dict(d[0]) | {"score": float(d[1]), "id": d[3]}
            for d in self.working_memory.declarative_memories
        ]
        procedural_report = [
            dict(d[0]) | {"score": float(d[1]), "id": d[3]}
            for d in self.working_memory.procedural_memories
        ]

        # why this response?
        why = MessageWhy(
            input=self.working_memory.user_message_json.text,
            intermediate_steps=[],
            memory={
                "episodic": episodic_report,
                "declarative": declarative_report,
                "procedural": procedural_report,
            },
            model_interactions=self.working_memory.model_interactions,
        )

        return why
    
    def load_working_memory_from_cache(self):
        """Load the working memory from the cache."""
        
        self.working_memory = \
            self.cache.get_value(f"{self.user_id}_working_memory") or WorkingMemory()

    def update_working_memory_cache(self):
        """Update the working memory in the cache."""

        updated_cache_item = CacheItem(f"{self.user_id}_working_memory", self.working_memory, -1)
        self.cache.insert(updated_cache_item)

    def send_ws_message(self, content: str | dict, msg_type: MSG_TYPES = "notification"):
        """Send a message via websocket.

        This method is useful for sending a message via websocket directly without passing through the LLM.  
        In case there is no connection the message is skipped and a warning is logged.

        Parameters
        ----------
        content : str
            The content of the message.
        msg_type : str
            The type of the message. Should be either `notification` (default), `chat`, `chat_token` or `error`

        Examples
        --------
        Send a notification via websocket
        >>> cat.send_ws_message("Hello, I'm a notification!")

        Send a chat message via websocket
        >>> cat.send_ws_message("Meooow!", msg_type="chat")
        
        Send an error message via websocket
        >>> cat.send_ws_message("Something went wrong", msg_type="error")

        Send custom data
        >>> cat.send_ws_message({"What day it is?": "It's my unbirthday"})
        """

        options = get_args(MSG_TYPES)

        if msg_type not in options:
            raise ValueError(
                f"The message type `{msg_type}` is not valid. Valid types: {', '.join(options)}"
            )

        if msg_type == "error":
            self.__send_ws_json(
                {"type": msg_type, "name": "GenericError", "description": str(content)}
            )
        else:
            self.__send_ws_json({"type": msg_type, "content": content})

    def send_chat_message(self, message: str | CatMessage, save=False):
        """Sends a chat message to the user using the active WebSocket connection.  
        In case there is no connection the message is skipped and a warning is logged

        Parameters
        ----------
        message: str, CatMessage
            Message to send
        save: bool | optional
            Save the message in the conversation history. Defaults to False.

        Examples
        --------
        Send a chat message during conversation from a hook, tool or form
        >>> cat.send_chat_message("Hello, dear!")

        Using a `CatMessage` object
        >>> message = CatMessage(text="Hello, dear!", user_id=cat.user_id)
        ... cat.send_chat_message(message)
        """

        if isinstance(message, str):
            why = self.__build_why()
            message = CatMessage(text=message, user_id=self.user_id, why=why)

        if save:
            self.working_memory.update_history(
                message
            )

        self.__send_ws_json(message.model_dump())

    def send_notification(self, content: str):
        """Sends a notification message to the user using the active WebSocket connection.  
        In case there is no connection the message is skipped and a warning is logged

        Parameters
        ----------
        content: str
            Message to send

        Examples
        --------
        Send a notification to the user
        >>> cat.send_notification("It's late!")
        """
        self.send_ws_message(content=content, msg_type="notification")

    def send_error(self, error: Union[str, Exception]):
        """Sends an error message to the user using the active WebSocket connection.

        In case there is no connection the message is skipped and a warning is logged

        Parameters
        ----------
        error: str, Exception
            Message to send

        Examples
        --------
        Send an error message to the user
        >>> cat.send_error("Something went wrong!")
        or
        >>> cat.send_error(CustomException("Something went wrong!"))
        """

        if isinstance(error, str):
            error_message = {
                "type": "error",
                "name": "GenericError",
                "description": str(error),
            }
        else:
            error_message = {
                "type": "error",
                "name": error.__class__.__name__,
                "description": str(error),
            }

        self.__send_ws_json(error_message)

    def recall_relevant_memories_to_working_memory(self, query=None):
        """Retrieve context from memory.

        The method retrieves the relevant memories from the vector collections that are given as context to the LLM.
        Recalled memories are stored in the working memory.

        Parameters
        ----------
        query : str, optional
            The query used to make a similarity search in the Cat's vector memories.  
            If not provided, the query will be derived from the last user's message.

        Examples
        --------
        Recall memories from custom query
        >>> cat.recall_relevant_memories_to_working_memory(query="What was written on the bottle?")

        Notes
        -----
        The user's message is used as a query to make a similarity search in the Cat's vector memories.
        Five hooks allow to customize the recall pipeline before and after it is done.

        See Also
        --------
        cat_recall_query
        before_cat_recalls_memories
        before_cat_recalls_episodic_memories
        before_cat_recalls_declarative_memories
        before_cat_recalls_procedural_memories
        after_cat_recalls_memories
        """

        recall_query = query

        if query is None:
            # If query is not provided, use the user's message as the query
            recall_query = self.working_memory.user_message_json.text

        # We may want to search in memory
        recall_query = self.mad_hatter.execute_hook(
            "cat_recall_query", recall_query, cat=self
        )
        log.info(f"Recall query: '{recall_query}'")

        # Embed recall query
        recall_query_embedding = self.embedder.embed_query(recall_query)
        self.working_memory.recall_query = recall_query

        # keep track of embedder model usage
        self.working_memory.model_interactions.append(
            EmbedderModelInteraction(
                prompt=[recall_query],
                source=utils.get_caller_info(skip=1),
                reply=recall_query_embedding, # TODO: should we avoid storing the embedding?
                input_tokens=len(tiktoken.get_encoding("cl100k_base").encode(recall_query)),
            )
        )

        # hook to do something before recall begins
        self.mad_hatter.execute_hook("before_cat_recalls_memories", cat=self)

        # Setting default recall configs for each memory
        # TODO: can these data structures become instances of a RecallSettings class?
        default_episodic_recall_config = {
            "embedding": recall_query_embedding,
            "k": 3,
            "threshold": 0.7,
            "metadata": {"source": self.user_id},
        }

        default_declarative_recall_config = {
            "embedding": recall_query_embedding,
            "k": 3,
            "threshold": 0.7,
            "metadata": {},
        }

        default_procedural_recall_config = {
            "embedding": recall_query_embedding,
            "k": 3,
            "threshold": 0.7,
            "metadata": {},
        }

        # hooks to change recall configs for each memory
        recall_configs = [
            self.mad_hatter.execute_hook(
                "before_cat_recalls_episodic_memories",
                default_episodic_recall_config,
                cat=self,
            ),
            self.mad_hatter.execute_hook(
                "before_cat_recalls_declarative_memories",
                default_declarative_recall_config,
                cat=self,
            ),
            self.mad_hatter.execute_hook(
                "before_cat_recalls_procedural_memories",
                default_procedural_recall_config,
                cat=self,
            ),
        ]

        memory_types = self.memory.vectors.collections.keys()

        for config, memory_type in zip(recall_configs, memory_types):
            memory_key = f"{memory_type}_memories"

            # recall relevant memories for collection
            vector_memory = getattr(self.memory.vectors, memory_type)
            memories = vector_memory.recall_memories_from_embedding(**config)

            setattr(
                self.working_memory, memory_key, memories
            )  # self.working_memory.procedural_memories = ...

        # hook to modify/enrich retrieved memories
        self.mad_hatter.execute_hook("after_cat_recalls_memories", cat=self)


    def llm(self, prompt: str, stream: bool = False) -> str:
        """Generate a response using the Large Language Model.

        Parameters
        ----------
        prompt : str
            The prompt for generating the response.
        stream : bool
            Whether to stream the tokens via websocket or not.

        Returns
        -------
        str
            The generated LLM response.

        Examples
        -------
        Detect profanity in a message
        >>> message = cat.working_memory.user_message_json.text
        ... cat.llm(f"Does this message contain profanity: '{message}'?  Reply with 'yes' or 'no'.")
        "no"

        Run the LLM and stream the tokens via websocket
        >>> cat.llm("Tell me which way to go?", stream=True)
        "It doesn't matter which way you go"
        """

        # should we stream the tokens?
        callbacks = []
        if stream:
            callbacks.append(NewTokenHandler(self))

        # Add a token counter to the callbacks
        caller = utils.get_caller_info(return_short=False)
        callbacks.append(ModelInteractionHandler(self, caller or "StrayCat"))

        # here we deal with motherfucking langchain
        prompt = ChatPromptTemplate(
            messages=[
                HumanMessage(content=prompt) # We decided to use HumanMessage for wide-range compatibility even if it could bring some problem with tokenizers
                # TODO: add here optional convo history passed to the method,
                #  or taken from working memory
            ]
        )

        chain = (
            prompt
            | RunnableLambda(lambda x: utils.langchain_log_prompt(x, f"{caller} prompt"))
            | self._llm
            | RunnableLambda(lambda x: utils.langchain_log_output(x, f"{caller} prompt output"))
            | StrOutputParser()
        )

        output = chain.invoke(
            {}, # in case we need to pass info to the template
            config=RunnableConfig(callbacks=callbacks)
        )

        return output

    def __call__(self, message_dict):
        """Run the conversation turn.

        This method is called on the user's message received from the client.  
        It is the main pipeline of the Cat, it is called automatically.

        Parameters
        ----------
        message_dict : dict
            Dictionary received from the client via http or websocket.

        Returns
        -------
        final_output : CatMessage
            CatMessage object, the Cat's answer to be sent back to the client.
        """

        # Impose user_id as the one authenticated
        # (ws message may contain a fake id)
        message_dict["user_id"] = self.user_id

        # Parse websocket message into UserMessage obj
        user_message = UserMessage.model_validate(message_dict)
        log.info(user_message)

        ### setup working memory for this convo turn
        # keeping track of model interactions
        self.working_memory.model_interactions = []
        # latest user message
        self.working_memory.user_message_json = user_message

        # Run a totally custom reply (skips all the side effects of the framework)
        fast_reply = self.mad_hatter.execute_hook(
            "fast_reply", {}, cat=self
        )
        if isinstance(fast_reply, CatMessage):
            return fast_reply
        if isinstance(fast_reply, dict) and "output" in fast_reply:
            return CatMessage(
                user_id=self.user_id, text=str(fast_reply["output"])
            )

        # hook to modify/enrich user input
        self.working_memory.user_message_json = self.mad_hatter.execute_hook(
            "before_cat_reads_message", self.working_memory.user_message_json, cat=self
        )

        # update conversation history (Human turn)
        self.working_memory.update_history(
            self.working_memory.user_message_json
        )

        # recall episodic and declarative memories from vector collections
        #   and store them in working_memory
        try:
            self.recall_relevant_memories_to_working_memory()
        except Exception:
            log.error("Error during recall.")

            err_message = "An error occurred while recalling relevant memories."

            return {
                "type": "error",
                "name": "VectorMemoryError",
                "description": err_message,
            }
        
        # reply with agent
        try:
            agent_output: AgentOutput = self.main_agent.execute(self)
        except Exception as e:
            # This error happens when the LLM
            #   does not respect prompt instructions.
            # We grab the LLM output here anyway, so small and
            #   non instruction-fine-tuned models can still be used.
            error_description = str(e)

            log.error(error_description)
            if "Could not parse LLM output: `" not in error_description:
                raise e

            unparsable_llm_output = error_description.replace(
                "Could not parse LLM output: `", ""
            ).replace("`", "")
            agent_output = AgentOutput(
                output=unparsable_llm_output,
            )

        log.info(agent_output)

        self._store_user_message_in_episodic_memory(
            self.working_memory.user_message_json.text
        )

        # why this response?
        why = self.__build_why()
        # TODO: should these assignations be included in self.__build_why ?
        why.intermediate_steps = agent_output.intermediate_steps
        why.agent_output = agent_output.model_dump()

        # prepare final cat message
        final_output = CatMessage(
            user_id=self.user_id, text=str(agent_output.output), why=why
        )

        # run message through plugins
        final_output = self.mad_hatter.execute_hook(
            "before_cat_sends_message", final_output, cat=self
        )

        # update conversation history (AI turn)
        self.working_memory.update_history(
            final_output
        )

        return final_output

    def run(self, user_message_json, return_message=False):
        try:
            # run main flow
            cat_message = self.__call__(user_message_json)
            # save working memory to cache
            self.update_working_memory_cache()

            if return_message:
                # return the message for HTTP usage
                return cat_message
            else:
                # send message back to client via WS
                self.send_chat_message(cat_message)
        except Exception as e:
            log.error(e)
            if return_message:
                return {"error": str(e)}
            else:
                try:
                    self.send_error(e)
                except ConnectionClosedOK as ex:
                    log.warning(ex)

    def classify(
        self, sentence: str, labels: List[str] | Dict[str, List[str]], score_threshold: float = 0.5
    ) -> str | None:
        """Classify a sentence.

        Parameters
        ----------
        sentence : str
            Sentence to be classified.
        labels : List[str] or Dict[str, List[str]]
            Possible output categories and optional examples.

        Returns
        -------
        label : str
            Sentence category.

        Examples
        -------
        >>> cat.classify("I feel good", labels=["positive", "negative"])
        "positive"

        Or giving examples for each category:

        >>> example_labels = {
        ...     "positive": ["I feel nice", "happy today"],
        ...     "negative": ["I feel bad", "not my best day"],
        ... }
        ... cat.classify("it is a bad day", labels=example_labels)
        "negative"

        """

        if isinstance(labels, dict):
            labels_names = labels.keys()
            examples_list = "\n\nExamples:"
            for label, examples in labels.items():
                for ex in examples:
                    examples_list += f'\n"{ex}" -> "{label}"'
        else:
            labels_names = labels
            examples_list = ""

        labels_list = '"' + '", "'.join(labels_names) + '"'

        prompt = f"""Classify this sentence:
"{sentence}"

Allowed classes are:
{labels_list}{examples_list}

"{sentence}" -> """

        response = self.llm(prompt)

        # find the closest match and its score with levenshtein distance
        best_label, score = min(
            ((label, utils.levenshtein_distance(response, label)) for label in labels_names),
            key=lambda x: x[1],
        )

        return best_label if score < score_threshold else None

    def langchainfy_chat_history(self, latest_n: int = 20) -> List[BaseMessage]:
        """Redirects to WorkingMemory.langchainfy_chat_history. Will be removed from this class in v2."""
        return self.working_memory.langchainfy_chat_history(latest_n)
    
    def stringify_chat_history(self, latest_n: int = 20) -> str:
        """Redirects to WorkingMemory.stringify_chat_history. Will be removed from this class in v2."""
        return self.working_memory.stringify_chat_history(latest_n)

    def _store_user_message_in_episodic_memory(self, user_message_text: str):
        doc = Document(
            page_content=user_message_text,
            metadata={"source": self.user_id, "when": time.time()},
        )
        doc = self.mad_hatter.execute_hook(
            "before_cat_stores_episodic_memory", doc, cat=self
        )
        # store user message in episodic memory
        # TODO: vectorize and store also conversation chunks
        #   (not raw dialog, but summarization)
        user_message_embedding = self.embedder.embed_documents([user_message_text])
        _ = self.memory.vectors.episodic.add_point(
            doc.page_content,
            user_message_embedding[0],
            doc.metadata,
        )

    @property
    def user_id(self) -> str:
        """The user's id.
        
        Returns
        -------
        user_id : str
            Current user's id.
        """
        return self.__user_id
    
    @property
    def user_data(self) -> AuthUserInfo:
        """`AuthUserInfo` object containing user data.

        Returns
        -------
        user_data : AuthUserInfo
            Current user's data.
        """
        return self.__user_data
    
    @property
    def _llm(self):
        """Instance of langchain `LLM`.
        Only use it if you directly want to deal with langchain, prefer method `cat.llm(prompt)` otherwise.
        """
        return CheshireCat()._llm

    @property
    def embedder(self):
        """Langchain `Embeddings` object.

        Returns
        -------
        embedder : langchain `Embeddings`
            Langchain embedder to turn text into a vector.


        Examples
        --------
        >>> cat.embedder.embed_query("Oh dear!")
        [0.2, 0.02, 0.4, ...]
        """
        return CheshireCat().embedder

    @property
    def memory(self):
        """Gives access to the long term memory, containing vector DB collections (episodic, declarative, procedural).

        Returns
        -------
        memory : LongTermMemory
            Long term memory of the Cat.


        Examples
        --------
        >>> cat.memory.vectors.episodic
        VectorMemoryCollection object for the episodic memory.
        """
        return CheshireCat().memory

    @property
    def rabbit_hole(self):
        """Gives access to the `RabbitHole`, to upload documents and URLs into the vector DB.

        Returns
        -------
        rabbit_hole : RabbitHole
            Module to ingest documents and URLs for RAG.


        Examples
        --------
        >>> cat.rabbit_hole.ingest_file(...)
        """
        return CheshireCat().rabbit_hole

    @property
    def mad_hatter(self):
        """Gives access to the `MadHatter` plugin manager.

        Returns
        -------
        mad_hatter : MadHatter
            Module to manage plugins.


        Examples
        --------

        Obtain the path in which your plugin is located
        >>> cat.mad_hatter.get_plugin().path
        /app/cat/plugins/my_plugin

        Obtain plugin settings
        >>> cat.mad_hatter.get_plugin().load_settings()
        {"num_cats": 44, "rows": 6, "remainder": 0}
        """
        return CheshireCat().mad_hatter

    @property
    def main_agent(self):
        """Gives access to the default main agent.
        """
        return CheshireCat().main_agent

    @property
    def white_rabbit(self):
        """Gives access to `WhiteRabbit`, to schedule repeatable tasks.

        Returns
        -------
        white_rabbit : WhiteRabbit
            Module to manage cron tasks via `APScheduler`.

        Examples
        --------
        Send a websocket message after 30 seconds
        >>> def ring_alarm_api():
        ...     cat.send_chat_message("It's late!")
        ...
        ... cat.white_rabbit.schedule_job(ring_alarm_api, seconds=30)
        """
        return CheshireCat().white_rabbit
    
    @property
    def cache(self):
        """Gives access to internal cache."""
        return CheshireCat().cache
