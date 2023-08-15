import time
from copy import deepcopy
import traceback

import langchain
import os
from cat.log import log
from cat.db.database import Database
from cat.rabbit_hole import RabbitHole
from cat.mad_hatter.mad_hatter import MadHatter
from cat.memory.working_memory import WorkingMemoryList
from cat.memory.long_term_memory import LongTermMemory
from cat.looking_glass.agent_manager import AgentManager


# main class
class CheshireCat:
    """The Cheshire Cat.

    This is the main class that manages everything.

    Attributes
    ----------
    web_socket_notifications : list
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
        self._embed_tools()

        # Agent manager instance (for reasoning)
        self.agent_manager = AgentManager(self)

        # Rabbit Hole Instance
        self.rabbit_hole = RabbitHole(self)

        # allows plugins to do something after the cat bootstrap is complete
        self.mad_hatter.execute_hook("after_cat_bootstrap")

        # queue of cat messages not directly related to last user input
        # i.e. finished uploading a file
        self.web_socket_notifications = []      

    def load_natural_language(self):
        """Load Natural Language related objects.

        The method exposes in the Cat all the NLP related stuff. Specifically, it sets the language models
        (LLM and Embedder) and the main prompt with default settings.

        Notes
        -----
        `use_episodic_memory`, `use_declarative_memory` and `use_procedural_memory` settings can be set from the admin
        GUI and allows to prevent the Cat from using any of the three vector memories.

        Warnings
        --------
        When using small Language Models it is suggested to turn off the memories and make the main prompt smaller
        to prevent them to fail.

        See Also
        --------
        get_language_model
        get_language_embedder
        agent_prompt_prefix
        """
        # LLM and embedder
        self._llm = self.mad_hatter.execute_hook("get_language_model")
        self.embedder = self.mad_hatter.execute_hook("get_language_embedder")

        # set the default prompt settings
        self.default_prompt_settings = {
            "prefix": "",
            "use_episodic_memory": True,
            "use_declarative_memory": True,
            "use_procedural_memory": True,
        }

    def load_memory(self):
        """Load LongTerMemory and WorkingMemory."""
        # Memory
        vector_memory_config = {"cat": self, "verbose": True}
        self.memory = LongTermMemory(vector_memory_config=vector_memory_config)
        
        # List working memory per user
        self.working_memory_list = WorkingMemoryList()
        
        # Load default shared working memory user
        self.working_memory = self.working_memory_list.get_working_memory()

    #realod plugins and embedd tools
    def load_plugins(self):
        self.mad_hatter.find_plugins()
        self._embed_tools()

    def install_plugin(self, package_plugin):
        self.mad_hatter.install_plugin(package_plugin)
        self._embed_tools()

    def uninstall_plugin(self, plugin_id):
        self.mad_hatter.uninstall_plugin(plugin_id)
        self._embed_tools()

    def toggle_plugin(self, plugin_id):
        self.mad_hatter.toggle_plugin(plugin_id)
        self._embed_tools()

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
        before_cat_recalls_memories
        before_cat_recalls_episodic_memories
        before_cat_recalls_declarative_memories
        before_cat_recalls_procedural_memories
        after_cat_recalls_memories
        """
        user_id = self.working_memory.get_user_id()
        user_message = self.working_memory["user_message_json"]["text"]
        prompt_settings = self.working_memory["user_message_json"]["prompt_settings"]

        # We may want to search in memory
        memory_query_text = self.mad_hatter.execute_hook("cat_recall_query", user_message)
        log(f'Recall query: "{memory_query_text}"')

        # Embed recall query
        memory_query_embedding = self.embedder.embed_query(memory_query_text)
        self.working_memory["memory_query"] = memory_query_text

        # hook to do something before recall begins
        self.mad_hatter.execute_hook("before_cat_recalls_memories")

        # Setting default recall configs for each memory
        default_episodic_recall_config = {
            "embedding": memory_query_embedding,
            "k": 3,
            "threshold": 0.7,
            "metadata": {"source": user_id},
        }

        default_declarative_recall_config = {
            "embedding": memory_query_embedding,
            "k": 3,
            "threshold": 0.7,
            "metadata": None,
        }

        default_procedural_recall_config = {
            "embedding": memory_query_embedding,
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
            setting = f"use_{memory_type}_memory"
            memory_key = f"{memory_type}_memories"

            if prompt_settings[setting]:
                # recall relevant memories
                vector_memory = getattr(self.memory.vectors, memory_type)
                memories = vector_memory.recall_memories_from_embedding(**config)

            else:
                memories = []

            self.working_memory[memory_key] = memories

        # hook to modify/enrich retrieved memories
        self.mad_hatter.execute_hook("after_cat_recalls_memories", memory_query_text)

    def llm(self, prompt: str) -> str:
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
        # Check if self._llm is a completion model and generate a response
        if isinstance(self._llm, langchain.llms.base.BaseLLM):
            return self._llm(prompt)

        # Check if self._llm is a chat model and call it as a completion model
        if isinstance(self._llm, langchain.chat_models.base.BaseChatModel):
            return self._llm.call_as_llm(prompt)

    def format_agent_input(self):
        """Format the input for the Agent.

        The method formats the strings of recalled memories and chat history that will be provided to the Langchain
        Agent and inserted in the prompt.

        Returns
        -------
        dict
            Formatted output to be parsed by the Agent executor.

        Notes
        -----
        The context of memories and conversation history is properly formatted before being parsed by the and, hence,
        information are inserted in the main prompt.
        All the formatting pipeline is hookable and memories can be edited.

        See Also
        --------
        agent_prompt_episodic_memories
        agent_prompt_declarative_memories
        agent_prompt_chat_history
        """
        # format memories to be inserted in the prompt
        episodic_memory_formatted_content = self.mad_hatter.execute_hook(
            "agent_prompt_episodic_memories",
            self.working_memory["episodic_memories"],
        )
        declarative_memory_formatted_content = self.mad_hatter.execute_hook(
            "agent_prompt_declarative_memories",
            self.working_memory["declarative_memories"],
        )

        # format conversation history to be inserted in the prompt
        conversation_history_formatted_content = self.mad_hatter.execute_hook(
            "agent_prompt_chat_history", self.working_memory["history"]
        )

        return {
            "input": self.working_memory["user_message_json"]["text"],
            "episodic_memory": episodic_memory_formatted_content,
            "declarative_memory": declarative_memory_formatted_content,
            "chat_history": conversation_history_formatted_content,
        }

    def store_new_message_in_working_memory(self, user_message_json):
        """Store message in working_memory and update the prompt settings.

        The method update the working memory with the last user's message.
        Also, the client sends the settings to turn on/off the vector memories.

        Parameters
        ----------
        user_message_json : dict
            Dictionary with the message received from the Websocket client

        """

        # store last message in working memory
        self.working_memory["user_message_json"] = user_message_json

        prompt_settings = deepcopy(self.default_prompt_settings)

        # override current prompt_settings with prompt settings sent via websocket (if any)
        prompt_settings.update(user_message_json.get("prompt_settings", {}))

        self.working_memory["user_message_json"]["prompt_settings"] = prompt_settings

    def _embed_tools(self):
        
        # retrieve from vectorDB all tool embeddings
        embedded_tools = self.memory.vectors.procedural.get_all_points()

        # easy acces to (point_id, tool_description)
        embedded_tools_ids = [t.id for t in embedded_tools]
        embedded_tools_descriptions = [t.payload["page_content"] for t in embedded_tools]

        # loop over mad_hatter tools
        for tool in self.mad_hatter.tools:
            # if the tool is not embedded 
            if tool.description not in embedded_tools_descriptions:
                # embed the tool and save it to DB
                self.memory.vectors.procedural.add_texts(
                    [tool.description],
                    [{
                        "source": "tool",
                        "when": time.time(),
                        "name": tool.name,
                        "docstring": tool.docstring
                    }],
                )

                log(f"Newly embedded tool: {tool.description}", "WARNING")
        
        # easy access to mad hatter tools (found in plugins)
        mad_hatter_tools_descriptions = [t.description for t in self.mad_hatter.tools]

        # loop over embedded tools and delete the ones not present in active plugins
        points_to_be_deleted = []
        for id, descr in zip(embedded_tools_ids, embedded_tools_descriptions):
            # if the tool is not active, it inserts it in the list of points to be deleted
            if descr not in mad_hatter_tools_descriptions:
                log(f"Deleting embedded tool: {descr}", "WARNING")
                points_to_be_deleted.append(id)

        # delete not active tools
        if len(points_to_be_deleted) > 0:
            self.memory.vectors.vector_db.delete(
                collection_name="procedural",
                points_selector=points_to_be_deleted
            )        

    def get_base_url(self):
        """Allows the Cat expose the base url."""
        secure = os.getenv('CORE_USE_SECURE_PROTOCOLS', '')
        if secure != '':
            secure = 's'
        return f'http{secure}://{os.environ["CORE_HOST"]}:{os.environ["CORE_PORT"]}'

    def get_base_path(self):
        """Allows the Cat expose the base path."""
        return "cat/"

    def get_plugin_path(self):
        """Allows the Cat expose the plugins path."""
        return os.path.join(self.get_base_path(), "plugins/")

    def get_static_url(self):
        """Allows the Cat expose the static server url."""
        return self.get_base_url() + "/static"
    
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
        log(user_message_json, "INFO")

        # Change working memory based on received user_id
        user_id = user_message_json.get('user_id', 'user')
        user_message_json['user_id'] = user_id
        self.working_memory = self.working_memory_list.get_working_memory(user_id)

        # hook to modify/enrich user input
        user_message_json = self.mad_hatter.execute_hook("before_cat_reads_message", user_message_json)

        # store user_message_json in working memory
        # it contains the new message, prompt settings and other info plugins may find useful
        self.store_new_message_in_working_memory(user_message_json)

        # TODO another hook here?

        # recall episodic and declarative memories from vector collections
        #   and store them in working_memory
        try:
            self.recall_relevant_memories_to_working_memory()
        except Exception as e:
            log(e, "ERROR")
            traceback.print_exc(e)

            err_message = (
                "Vector memory error: you probably changed "
                "Embedder and old vector memory is not compatible. "
                "Please delete `core/long_term_memory` folder."
            )
            return {
                "error": False,
                # TODO: Otherwise the frontend gives notice of the error
                #   but does not show what the error is
                "content": err_message,
                "why": {},
            }

        # prepare input to be passed to the agent.
        #   Info will be extracted from working memory
        agent_input = self.format_agent_input()

        # reply with agent
        try:
            cat_message = self.agent_manager.execute_agent(agent_input)
        except Exception as e:
            # This error happens when the LLM
            #   does not respect prompt instructions.
            # We grab the LLM output here anyway, so small and
            #   non instruction-fine-tuned models can still be used.
            error_description = str(e)
            log("LLM does not respect prompt instructions", "ERROR")
            log(error_description, "ERROR")
            if not "Could not parse LLM output: `" in error_description:
                raise e

            unparsable_llm_output = error_description.replace("Could not parse LLM output: `", "").replace("`", "")
            cat_message = {
                "input": agent_input["input"],
                "intermediate_steps": [],
                "output": unparsable_llm_output
            }

        log("cat_message:", "DEBUG")
        log(cat_message, "DEBUG")

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
            "error": False,
            "type": "chat",
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
