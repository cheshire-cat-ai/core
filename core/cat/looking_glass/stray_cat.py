import time
import asyncio
import traceback
from typing import Literal, get_args

from langchain.docstore.document import Document
from langchain_community.llms import BaseLLM
from langchain_core.language_models.chat_models import BaseChatModel

from fastapi import WebSocket

from cat.log import log
from cat.looking_glass.cheshire_cat import CheshireCat
from cat.looking_glass.callbacks import NewTokenHandler
from cat.memory.working_memory import WorkingMemory


MAX_TEXT_INPUT = 2000
MSG_TYPES = Literal["notification", "chat", "error", "chat_token"]

# The Stray cat goes around tools and hook, making troubles
class StrayCat:
    """User/session based object containing working memory and a few utility pointers"""

    def __init__(
            self,
            user_id: str,
            main_loop,
            ws: WebSocket = None,
        ):
        self.__user_id = user_id
        self.__ws_messages = asyncio.Queue()
        self.working_memory = WorkingMemory()

        # attribute to store ws connection
        self.ws = ws

        self.__main_loop = main_loop

        self.__loop = asyncio.new_event_loop()

    def send_ws_message(self, content: str, msg_type: MSG_TYPES="notification"):
        
        """Send a message via websocket.

        This method is useful for sending a message via websocket directly without passing through the LLM

        Parameters
        ----------
        content : str
            The content of the message.
        msg_type : str
            The type of the message. Should be either `notification`, `chat`, `chat_token` or `error`
        """

        if self.ws is None:
            log.warning(f"No websocket connection is open for user {self.user_id}")
            return

        options = get_args(MSG_TYPES)

        if msg_type not in options:
            raise ValueError(f"The message type `{msg_type}` is not valid. Valid types: {', '.join(options)}")

        if msg_type == "error":

            # Call put_nowait in the uvicorn main loop is necessary
            # as the ws_mesages queue

            self.__main_loop.call_soon_threadsafe(
                self.__ws_messages.put_nowait,
                {
                    "type": msg_type,
                    "name": "GenericError",
                    "description": content
                }
            )
        else:
            self.__main_loop.call_soon_threadsafe(
                self.__ws_messages.put_nowait,
                {
                    "type": msg_type,
                    "content": content
                }
            )

    def recall_relevant_memories_to_working_memory(self, query=None):
        """Retrieve context from memory.

        The method retrieves the relevant memories from the vector collections that are given as context to the LLM.
        Recalled memories are stored in the working memory.

        Parameters
        ----------
        query : str, optional
        The query used to make a similarity search in the Cat's vector memories. If not provided, the query
        will be derived from the user's message.

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
            recall_query = self.working_memory["user_message_json"]["text"]

        # We may want to search in memory
        recall_query = self.mad_hatter.execute_hook("cat_recall_query", recall_query, cat=self)
        log.info(f"Recall query: '{recall_query}'")

        # Embed recall query
        recall_query_embedding = self.embedder.embed_query(recall_query)
        self.working_memory["recall_query"] = recall_query

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
            "metadata": None,
        }

        default_procedural_recall_config = {
            "embedding": recall_query_embedding,
            "k": 3,
            "threshold": 0.7,
            "metadata": None,
        }

        # hooks to change recall configs for each memory
        recall_configs = [
            self.mad_hatter.execute_hook(
                "before_cat_recalls_episodic_memories", default_episodic_recall_config, cat=self),
            self.mad_hatter.execute_hook(
                "before_cat_recalls_declarative_memories", default_declarative_recall_config, cat=self),
            self.mad_hatter.execute_hook(
                "before_cat_recalls_procedural_memories", default_procedural_recall_config, cat=self)
        ]

        memory_types = self.memory.vectors.collections.keys()

        for config, memory_type in zip(recall_configs, memory_types):
            memory_key = f"{memory_type}_memories"

            # recall relevant memories for collection
            vector_memory = getattr(self.memory.vectors, memory_type)
            memories = vector_memory.recall_memories_from_embedding(**config)

            self.working_memory[memory_key] = memories

        # hook to modify/enrich retrieved memories
        self.mad_hatter.execute_hook("after_cat_recalls_memories", cat=self)

    def llm(self, prompt: str, stream: bool = False) -> str:
        """Generate a response using the LLM model.

        This method is useful for generating a response with both a chat and a completion model using the same syntax

        Parameters
        ----------
        prompt : str
            The prompt for generating the response.

        Returns
        -------
        str
            The generated response.

        """

        # should we stream the tokens?
        callbacks = []
        if stream:
            callbacks.append(NewTokenHandler(self))

        # Check if self._llm is a completion model and generate a response
        if isinstance(self._llm, BaseLLM):
            return self._llm(prompt, callbacks=callbacks)

        # Check if self._llm is a chat model and call it as a completion model
        if isinstance(self._llm, BaseChatModel):
            return self._llm.call_as_llm(prompt, callbacks=callbacks)

    async def __call__(self, user_message_json):
            """Call the Cat instance.

            This method is called on the user's message received from the client.

            Parameters
            ----------
            user_message_json : dict
                Dictionary received from the Websocket client.

            Returns
            -------
            final_output : dict
                Dictionary with the Cat's answer to be sent to the client.

            Notes
            -----
            Here happens the main pipeline of the Cat. Namely, the Cat receives the user's input and recall the memories.
            The retrieved context is formatted properly and given in input to the Agent that uses the LLM to produce the
            answer. This is formatted in a dictionary to be sent as a JSON via Websocket to the client.

            """
            log.info(user_message_json)

            # set a few easy access variables
            self.working_memory["user_message_json"] = user_message_json

            # hook to modify/enrich user input
            self.working_memory["user_message_json"] = self.mad_hatter.execute_hook(
                "before_cat_reads_message",
                self.working_memory["user_message_json"],
                cat=self
            )

            if len(user_message_json["text"]) > MAX_TEXT_INPUT:
                # TODO: reflex hook!
                self.send_long_message_to_declarative()

            # recall episodic and declarative memories from vector collections
            #   and store them in working_memory
            try:
                self.recall_relevant_memories_to_working_memory()
            except Exception as e:
                log.error(e)
                traceback.print_exc(e)

                err_message = (
                    "You probably changed Embedder and old vector memory is not compatible. "
                    "Please delete `core/long_term_memory` folder."
                )

                return {
                    "type": "error",
                    "name": "VectorMemoryError",
                    "description": err_message,
                }
            
            # reply with agent
            try:
                cat_message = await self.agent_manager.execute_agent(self)
            except Exception as e:
                # This error happens when the LLM
                #   does not respect prompt instructions.
                # We grab the LLM output here anyway, so small and
                #   non instruction-fine-tuned models can still be used.
                error_description = str(e)

                log.error(error_description)
                if "Could not parse LLM output: `" not in error_description:
                    raise e

                unparsable_llm_output = error_description.replace("Could not parse LLM output: `", "").replace("`", "")
                cat_message = {
                    "input": self.working_memory["user_message_json"]["text"],
                    "intermediate_steps": [],
                    "output": unparsable_llm_output
                }

            log.info("cat_message:")
            log.info(cat_message)

            user_message = self.working_memory["user_message_json"]["text"]

            doc = Document(
                page_content=user_message,
                metadata={
                    "source": self.user_id,
                    "when": time.time()
                }
            )
            doc = self.mad_hatter.execute_hook(
                "before_cat_stores_episodic_memory", doc, cat=self
            )
            # store user message in episodic memory
            # TODO: vectorize and store also conversation chunks
            #   (not raw dialog, but summarization)
            user_message_embedding = self.embedder.embed_documents([user_message])
            _ = self.memory.vectors.episodic.add_point(
                doc.page_content,
                user_message_embedding[0],
                doc.metadata,
            )

            # build data structure for output (response and why with memories)
            # TODO: these 3 lines are a mess, simplify
            episodic_report = [dict(d[0]) | {"score": float(d[1]), "id": d[3]} for d in self.working_memory["episodic_memories"]]
            declarative_report = [dict(d[0]) | {"score": float(d[1]), "id": d[3]} for d in self.working_memory["declarative_memories"]]
            procedural_report = [dict(d[0]) | {"score": float(d[1]), "id": d[3]} for d in self.working_memory["procedural_memories"]]
            
            final_output = {
                "type": "chat",
                "user_id": self.user_id,
                "content": str(cat_message.get("output")),
                "why": {
                    "input": cat_message.get("input"),
                    "intermediate_steps": cat_message.get("intermediate_steps", []),
                    "memory": {
                        "episodic": episodic_report,
                        "declarative": declarative_report,
                        "procedural": procedural_report,
                    },
                },
            }

            final_output = self.mad_hatter.execute_hook("before_cat_sends_message", final_output, cat=self)

            # update conversation history
            self.working_memory.update_conversation_history(who="Human", message=user_message)
            self.working_memory.update_conversation_history(who="AI", message=final_output["content"], why=final_output["why"])

            return final_output

    def run(self, user_message_json):
        return self.loop.run_until_complete(
            self.__call__(user_message_json)
        )

    def send_long_message_to_declarative(self):
        #Split input after MAX_TEXT_INPUT tokens, on a whitespace, if any, and send it to the rabbit hole
        index = MAX_TEXT_INPUT
        query = self.working_memory["user_message_json"]["text"]
        char = query[index]
        while not char.isspace() and index > 0:
            index -= 1
            char = query[index]
        if index <= 0:
            index = MAX_TEXT_INPUT
        query, to_declarative_memory = query[:index], query
        self.working_memory["user_message_json"]["text"] = query # shortens working memory content

        # TODO: can we run ingestion in the background?
        docs = self.rabbit_hole.string_to_docs(
            stray=self,
            file_bytes=to_declarative_memory,
            content_type="text/plain"
        )
        self.rabbit_hole.store_documents(self, docs=docs, source="")

    @property
    def user_id(self):
        return self.__user_id

    @property
    def _llm(self):
        return CheshireCat()._llm
    
    @property
    def embedder(self):
        return CheshireCat().embedder
    
    @property
    def memory(self):
        return CheshireCat().memory

    @property
    def rabbit_hole(self):
        return CheshireCat().rabbit_hole

    @property
    def mad_hatter(self):
        return CheshireCat().mad_hatter
    
    @property
    def agent_manager(self):
        return CheshireCat().agent_manager

    @property
    def loop(self):
        return self.__loop