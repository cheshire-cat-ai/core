import time
import traceback

import langchain
from cat.log import log
from cat.db.database import get_db_session, create_db_and_tables
from cat.rabbit_hole import RabbitHole
from cat.mad_hatter.mad_hatter import MadHatter
from cat.memory.working_memory import WorkingMemory
from cat.memory.long_term_memory import LongTermMemory
from cat.looking_glass.agent_manager import AgentManager


# main class
class CheshireCat:
    def __init__(self):
        # access to DB
        self.load_db()

        # bootstrap the cat!
        self.bootstrap()

        # queue of cat messages not directly related to last user input
        # i.e. finished uploading a file
        self.web_socket_notifications = []

    def bootstrap(self):
        """This method is called when the cat is instantiated and
        has to be called whenever LLM, embedder,
        agent or memory need to be reinstantiated
        (for example an LLM change at runtime)
        """

        # reinstantiate MadHatter (reloads all plugins' hooks and tools)
        self.load_plugins()

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

    def load_db(self):
        # if there is no db, create it
        create_db_and_tables()

        # access db from instance
        self.db = get_db_session

    def load_natural_language(self):
        # LLM and embedder
        self.llm = self.mad_hatter.execute_hook("get_language_model")
        self.embedder = self.mad_hatter.execute_hook("get_language_embedder")

        # HyDE chain
        hypothesis_prompt = langchain.PromptTemplate(
            input_variables=["input"],
            template=self.mad_hatter.execute_hook("hypothetical_embedding_prompt"),
        )

        self.hypothetis_chain = langchain.chains.LLMChain(prompt=hypothesis_prompt, llm=self.llm)

        self.summarization_prompt = self.mad_hatter.execute_hook("summarization_prompt")

        # custom summarization chain
        self.summarization_chain = langchain.chains.LLMChain(
            llm=self.llm,
            verbose=False,
            prompt=langchain.PromptTemplate(template=self.summarization_prompt, input_variables=["text"]),
        )

    def load_memory(self):
        # Memory
        vector_memory_config = {"cat": self, "verbose": True}
        self.memory = LongTermMemory(vector_memory_config=vector_memory_config)
        self.working_memory = WorkingMemory()

    def load_plugins(self):
        # Load plugin system
        self.mad_hatter = MadHatter(self)

    def recall_relevant_memories_to_working_memory(self, user_message):
        # hook to do something before recall begins
        self.mad_hatter.execute_hook("before_cat_recalls_memories", user_message)

        # We may want to search in memory
        memory_query_text = self.mad_hatter.execute_hook("cat_recall_query", user_message)
        log(f'Recall query: "{memory_query_text}"')

        # embed recall query
        memory_query_embedding = self.embedder.embed_query(memory_query_text)
        self.working_memory["memory_query"] = memory_query_text

        # recall relevant memories (episodic)
        episodic_memories = self.memory.vectors.episodic.recall_memories_from_embedding(
            embedding=memory_query_embedding
        )
        self.working_memory["episodic_memories"] = episodic_memories

        # recall relevant memories (declarative)
        declarative_memories = self.memory.vectors.declarative.recall_memories_from_embedding(
            embedding=memory_query_embedding
        )
        self.working_memory["declarative_memories"] = declarative_memories

        # hook to modify/enrich retrieved memories
        self.mad_hatter.execute_hook("after_cat_recalled_memories", memory_query_text)

    def format_agent_executor_input(self):
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
            "ai_prefix": "AI",
        }

    def __call__(self, user_message_json):
        log(user_message_json, "DEBUG")

        # hook to modify/enrich user input
        user_message_json = self.mad_hatter.execute_hook("before_cat_reads_message", user_message_json)

        # store user_message_json in working memory
        self.working_memory["user_message_json"] = user_message_json

        # extract actual user message text
        user_message = user_message_json["text"]

        # recall episodic and declarative memories from vector collections
        #   and store them in working_memory
        try:
            self.recall_relevant_memories_to_working_memory(user_message)
        except Exception as e:
            log(e)
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

        # prepare input to be passed to the agent executor.
        #   Info will be extracted from working memory
        agent_executor_input = self.format_agent_executor_input()

        # load agent (will rebuild both agent and agent_executor
        #   based on context and plugins)
        agent_executor = self.agent_manager.get_agent_executor()

        # reply with agent
        try:
            cat_message = agent_executor(agent_executor_input)
        except Exception as e:
            # This error happens when the LLM
            #   does not respect prompt instructions.
            # We grab the LLM outptu here anyway, so small and
            #   non instruction-fine-tuned models can still be used.
            error_description = str(e)
            if not "Could not parse LLM output: `" in error_description:
                raise e

            unparsable_llm_output = error_description.replace("Could not parse LLM output: `", "").replace("`", "")
            cat_message = {"output": unparsable_llm_output}

        log(cat_message, "DEBUG")

        # update conversation history
        self.working_memory.update_conversation_history(who="Human", message=user_message)
        self.working_memory.update_conversation_history(who="AI", message=cat_message["output"])

        # store user message in episodic memory
        # TODO: vectorize and store also conversation chunks
        #   (not raw dialog, but summarization)
        _ = self.memory.vectors.episodic.add_texts(
            [user_message],
            [{"source": "user", "when": time.time()}],
        )

        # build data structure for output (response and why with memories)
        episodic_report = [dict(d[0]) | {"score": float(d[1])} for d in self.working_memory["episodic_memories"]]
        declarative_report = [dict(d[0]) | {"score": float(d[1])} for d in self.working_memory["declarative_memories"]]
        final_output = {
            "error": False,
            "type": "chat",
            "content": cat_message.get("output"),
            "why": {
                "input": cat_message.get("input"),
                "intermediate_steps": cat_message.get("intermediate_steps"),
                "memory": {
                    "vectors": {
                        "episodic": episodic_report,
                        "declarative": declarative_report,
                    }
                },
            },
        }

        final_output = self.mad_hatter.execute_hook("before_cat_sends_message", final_output)

        return final_output
