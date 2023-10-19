import time
from copy import deepcopy
import traceback
from typing import Literal, get_args
import os
import asyncio
import langchain
from langchain.llms import Cohere, OpenAI, AzureOpenAI, HuggingFaceTextGenInference, HuggingFaceHub
from langchain.chat_models import ChatOpenAI, AzureChatOpenAI
from langchain.base_language import BaseLanguageModel

from cat.log import log
from cat.db import crud
from cat.db.database import Database
from cat.rabbit_hole import RabbitHole
from cat.mad_hatter.mad_hatter import MadHatter
from cat.memory.working_memory import WorkingMemoryList
from cat.memory.long_term_memory import LongTermMemory
from cat.looking_glass.agent_manager import AgentManager
from cat.looking_glass.callbacks import NewTokenHandler
import cat.factory.llm as llms
import cat.factory.embedder as embedders
from cat.factory.custom_llm import CustomOpenAI


MSG_TYPES = Literal["notification", "chat", "error", "chat_token"]

# main class
class CheshireCat:
    """The Cheshire Cat.

    This is the main class that manages everything.

    Attributes
    ----------
    ws_messages : list
        List of notifications to be sent to the frontend.

    """

    def __init__(self):
        """Cat initialization.

        At init time the Cat executes the bootstrap.
        """

        # bootstrap the cat!
        # reinstantiate MadHatter (reloads all plugins' hooks and tools)
        self.mad_hatter = MadHatter(self)

        # allows plugins to do something before cat components are loaded
        self.mad_hatter.execute_hook("before_cat_bootstrap")

        # load LLM and embedder
        self.load_natural_language()

        # Load memories (vector collections and working_memory)
        self.load_memory()

        # After memory is loaded, we can get/create tools embeddings
        self.mad_hatter.embed_tools()

        # Agent manager instance (for reasoning)
        self.agent_manager = AgentManager(self)

        # Rabbit Hole Instance
        self.rabbit_hole = RabbitHole(self)

        # allows plugins to do something after the cat bootstrap is complete
        self.mad_hatter.execute_hook("after_cat_bootstrap")

        # queue of cat messages not directly related to last user input
        # i.e. finished uploading a file
        self.ws_messages = asyncio.Queue()     

    def load_natural_language(self):
        """Load Natural Language related objects.

        The method exposes in the Cat all the NLP related stuff. Specifically, it sets the language models
        (LLM and Embedder).

        Warnings
        --------
        When using small Language Models it is suggested to turn off the memories and make the main prompt smaller
        to prevent them to fail.

        See Also
        --------
        agent_prompt_prefix
        """
        # LLM and embedder
        self._llm = self.get_language_model()
        self.embedder = self.get_language_embedder()

    def get_language_model(self) -> BaseLanguageModel:
        """Large Language Model (LLM) selection at bootstrap time.

        Returns
        -------
        llm : BaseLanguageModel
            Langchain `BaseLanguageModel` instance of the selected model.

        Notes
        -----
        Bootstrapping is the process of loading the plugins, the natural language objects (e.g. the LLM), the memories,
        the *Agent Manager* and the *Rabbit Hole*.

        """
        selected_llm = crud.get_setting_by_name(name="llm_selected")

        if selected_llm is None:
            # return default LLM
            llm = llms.LLMDefaultConfig.get_llm_from_config({})

        else:
            # get LLM factory class
            selected_llm_class = selected_llm["value"]["name"]
            FactoryClass = getattr(llms, selected_llm_class)

            # obtain configuration and instantiate LLM
            selected_llm_config = crud.get_setting_by_name(name=selected_llm_class)
            try:
                llm = FactoryClass.get_llm_from_config(selected_llm_config["value"])
            except Exception as e:
                import traceback
                traceback.print_exc()
                llm = llms.LLMDefaultConfig.get_llm_from_config({})

        return llm


    def get_language_embedder(self) -> embedders.EmbedderSettings:
        """Hook into the  embedder selection.

        Allows to modify how the Cat selects the embedder at bootstrap time.

        Bootstrapping is the process of loading the plugins, the natural language objects (e.g. the LLM),
        the memories, the *Agent Manager* and the *Rabbit Hole*.

        Parameters
        ----------
        cat: CheshireCat
            Cheshire Cat instance.

        Returns
        -------
        embedder : Embeddings
            Selected embedder model.
        """
        # Embedding LLM

        selected_embedder = crud.get_setting_by_name(name="embedder_selected")

        if selected_embedder is not None:
            # get Embedder factory class
            selected_embedder_class = selected_embedder["value"]["name"]
            FactoryClass = getattr(embedders, selected_embedder_class)

            # obtain configuration and instantiate Embedder
            selected_embedder_config = crud.get_setting_by_name(name=selected_embedder_class)
            embedder = FactoryClass.get_embedder_from_config(selected_embedder_config["value"])

            return embedder

        # OpenAI embedder
        if type(self._llm) in [OpenAI, ChatOpenAI]:
            embedder = embedders.EmbedderOpenAIConfig.get_embedder_from_config(
                {
                    "openai_api_key": self._llm.openai_api_key,
                }
            )

        # Azure
        elif type(self._llm) in [AzureOpenAI, AzureChatOpenAI]:
            embedder = embedders.EmbedderAzureOpenAIConfig.get_embedder_from_config(
                {
                    "openai_api_key": self._llm.openai_api_key,
                    "openai_api_type": "azure",
                    "model": "text-embedding-ada-002",
                    # Now the only model for embeddings is text-embedding-ada-002
                    # It is also possible to use the Azure "deployment" name that is user defined
                    # when the model is deployed to Azure.
                    # "deployment": "my-text-embedding-ada-002",
                    "openai_api_base": self._llm.openai_api_base,
                    # https://learn.microsoft.com/en-us/azure/cognitive-services/openai/reference#embeddings
                    # current supported versions 2022-12-01,2023-03-15-preview, 2023-05-15
                    # Don't mix api versions https://github.com/hwchase17/langchain/issues/4775
                    "openai_api_version": "2023-05-15",
                }
            )

        # Cohere
        elif type(self._llm) in [Cohere]:
            embedder = embedders.EmbedderCohereConfig.get_embedder_from_config(
                {
                    "cohere_api_key": self._llm.cohere_api_key,
                    "model": "embed-multilingual-v2.0",
                    # Now the best model for embeddings is embed-multilingual-v2.0
                }
            )

        # HuggingFace
        elif type(self._llm) in [HuggingFaceHub]:
            embedder = embedders.EmbedderHuggingFaceHubConfig.get_embedder_from_config(
                {
                    "huggingfacehub_api_token": self._llm.huggingfacehub_api_token,
                    "repo_id": "sentence-transformers/all-mpnet-base-v2",
                }
            )

        # Llama-cpp-python
        elif type(self._llm) in [CustomOpenAI]:
            embedder = embedders.EmbedderLlamaCppConfig.get_embedder_from_config(
                {
                    "url": self._llm.url
                }
            )

        else:
            # If no embedder matches vendor, and no external embedder is configured, we use the DumbEmbedder.
            #   `This embedder is not a model properly trained
            #    and this makes it not suitable to effectively embed text,
            #    "but it does not know this and embeds anyway".` - cit. Nicola Corbellini
            embedder = embedders.EmbedderDumbConfig.get_embedder_from_config({})

        return embedder

    def load_memory(self):
        """Load LongTerMemory and WorkingMemory."""
        # Memory
        vector_memory_config = {"cat": self, "verbose": True}
        self.memory = LongTermMemory(vector_memory_config=vector_memory_config)
        
        # List working memory per user
        self.working_memory_list = WorkingMemoryList()
        
        # Load default shared working memory user
        self.working_memory = self.working_memory_list.get_working_memory()

    def recall_relevant_memories_to_working_memory(self):
        """Retrieve context from memory.

        The method retrieves the relevant memories from the vector collections that are given as context to the LLM.
        Recalled memories are stored in the working memory.

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
        user_id = self.working_memory.get_user_id()
        recall_query = self.working_memory["user_message_json"]["text"]

        # We may want to search in memory
        recall_query = self.mad_hatter.execute_hook("cat_recall_query", recall_query)
        log.info(f'Recall query: "{recall_query}"')

        # Embed recall query
        recall_query_embedding = self.embedder.embed_query(recall_query)
        self.working_memory["recall_query"] = recall_query

        # hook to do something before recall begins
        self.mad_hatter.execute_hook("before_cat_recalls_memories")

        # Setting default recall configs for each memory
        # TODO: can these data structrues become instances of a RecallSettings class?
        default_episodic_recall_config = {
            "embedding": recall_query_embedding,
            "k": 3,
            "threshold": 0.7,
            "metadata": {"source": user_id},
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
            self.mad_hatter.execute_hook("before_cat_recalls_episodic_memories", default_episodic_recall_config),
            self.mad_hatter.execute_hook("before_cat_recalls_declarative_memories", default_procedural_recall_config),
            self.mad_hatter.execute_hook("before_cat_recalls_procedural_memories", default_declarative_recall_config)
        ]

        memory_types = self.memory.vectors.collections.keys()

        for config, memory_type in zip(recall_configs, memory_types):
            memory_key = f"{memory_type}_memories"

            # recall relevant memories for collection
            vector_memory = getattr(self.memory.vectors, memory_type)
            memories = vector_memory.recall_memories_from_embedding(**config)

            self.working_memory[memory_key] = memories

        # hook to modify/enrich retrieved memories
        self.mad_hatter.execute_hook("after_cat_recalls_memories")

    def llm(self, prompt: str, chat: bool = False, stream: bool = False) -> str:
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
        if isinstance(self._llm, langchain.llms.base.BaseLLM):
            return self._llm(prompt, callbacks=callbacks)

        # Check if self._llm is a chat model and call it as a completion model
        if isinstance(self._llm, langchain.chat_models.base.BaseChatModel):
            return self._llm.call_as_llm(prompt, callbacks=callbacks)

    def send_ws_message(self, content: str, msg_type: MSG_TYPES = "notification"):
        """Send a message via websocket.

        This method is useful for sending a message via websocket directly without passing through the LLM

        Parameters
        ----------
        content : str
            The content of the message.
        msg_type : str
            The type of the message. Should be either `notification`, `chat` or `error`
        """

        options = get_args(MSG_TYPES)

        if msg_type not in options:
            raise ValueError(f"The message type `{msg_type}` is not valid. Valid types: {', '.join(options)}")

        if msg_type == "error":
            asyncio.run(
                self.ws_messages.put( 
                    {
                        "type": msg_type,
                        "name": "GenericError",
                        "description": content
                    }
                )
            )
        else:
            asyncio.run(
                self.ws_messages.put(
                    {
                        "type": msg_type,
                        "content": content
                    }
                )
            )    

    def get_base_url(self):
        """Allows the Cat expose the base url."""
        secure = os.getenv('CORE_USE_SECURE_PROTOCOLS', '')
        if secure != '':
            secure = 's'
        return f'http{secure}://{os.environ["CORE_HOST"]}:{os.environ["CORE_PORT"]}/'

    def get_base_path(self):
        """Allows the Cat expose the base path."""
        return "cat/"

    def get_plugin_path(self):
        """Allows the Cat expose the plugins path."""
        return os.path.join(self.get_base_path(), "plugins/")

    def get_static_url(self):
        """Allows the Cat expose the static server url."""
        return self.get_base_url() + "static/"
    
    def get_static_path(self):
        """Allows the Cat expose the static files path."""
        return os.path.join(self.get_base_path(), "static/")

    def __call__(self, user_message_json):
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

        # Change working memory based on received user_id
        user_id = user_message_json.get('user_id', 'user')
        user_message_json['user_id'] = user_id
        self.working_memory = self.working_memory_list.get_working_memory(user_id)

        # hook to modify/enrich user input
        user_message_json = self.mad_hatter.execute_hook("before_cat_reads_message", user_message_json)

        # store last message in working memory
        self.working_memory["user_message_json"] = user_message_json

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
            cat_message = self.agent_manager.execute_agent()
        except Exception as e:
            # This error happens when the LLM
            #   does not respect prompt instructions.
            # We grab the LLM output here anyway, so small and
            #   non instruction-fine-tuned models can still be used.
            error_description = str(e)

            log.error(error_description)
            if not "Could not parse LLM output: `" in error_description:
                raise e

            unparsable_llm_output = error_description.replace("Could not parse LLM output: `", "").replace("`", "")
            cat_message = {
                "input": self.working_memory["user_message_json"]["text"],
                "intermediate_steps": [],
                "output": unparsable_llm_output
            }

        log.info("cat_message:")
        log.info(cat_message)

        # update conversation history
        user_message = self.working_memory["user_message_json"]["text"]
        self.working_memory.update_conversation_history(who="Human", message=user_message)
        self.working_memory.update_conversation_history(who="AI", message=cat_message["output"])

        # store user message in episodic memory
        # TODO: vectorize and store also conversation chunks
        #   (not raw dialog, but summarization)
        _ = self.memory.vectors.episodic.add_texts(
            [user_message],
            [{"source": user_id, "when": time.time()}],
        )

        # build data structure for output (response and why with memories)
        episodic_report = [dict(d[0]) | {"score": float(d[1]), "id": d[3]} for d in self.working_memory["episodic_memories"]]
        declarative_report = [dict(d[0]) | {"score": float(d[1]), "id": d[3]} for d in self.working_memory["declarative_memories"]]
        procedural_report = [dict(d[0]) | {"score": float(d[1]), "id": d[3]} for d in self.working_memory["procedural_memories"]]
        
        final_output = {
            "type": "chat",
            "user_id": user_id,
            "content": cat_message.get("output"),
            "why": {
                "input": cat_message.get("input"),
                "intermediate_steps": cat_message.get("intermediate_steps"),
                "memory": {
                    "episodic": episodic_report,
                    "declarative": declarative_report,
                    "procedural": procedural_report,
                },
            },
        }

        final_output = self.mad_hatter.execute_hook("before_cat_sends_message", final_output)

        return final_output
