import time

import langchain
from cat.utils import log
from cat.memory import VectorStore, VectorMemoryConfig
from cat.agent_manager import AgentManager
from cat.mad_hatter.mad_hatter import MadHatter


# main class representing the cat
class CheshireCat:
    def __init__(self, settings):
        self.settings = settings

        # bootstrap the cat!
        self.load_plugins()
        self.load_agent()

    def load_plugins(self):
        # recent conversation # TODO: load from episodic memory latest conversation messages
        self.history = ""

        # Load plugin system
        self.mad_hatter = MadHatter()

        # LLM and embedder
        # TODO: llm and embedder config should be loaded from db after the user has set them up
        # TODO: remove .env configuration
        self.llm = self.mad_hatter.execute_hook("get_language_model")
        self.embedder = self.mad_hatter.execute_hook("get_language_embedder")

        # Prompts
        self.prefix_prompt = self.mad_hatter.execute_hook("get_main_prompt_prefix")
        self.suffix_prompt = self.mad_hatter.execute_hook("get_main_prompt_suffix")

        # Memory
        self.vector_store = VectorStore(
            VectorMemoryConfig(verbose=self.settings.verbose)
        )
        episodic_memory = self.vector_store.get_vector_store(
            "episodes", embedder=self.embedder
        )
        declarative_memory = self.vector_store.get_vector_store(
            "documents", embedder=self.embedder
        )
        self.memory = {"episodes": episodic_memory, "documents": declarative_memory}
        # TODO: don't know if it is better to use different collections or just different metadata

        # HyDE chain
        hypothesis_prompt = langchain.PromptTemplate(
            input_variables=["input"],
            template=self.mad_hatter.execute_hook("get_hypothetical_embedding_prompt"),
        )

        self.hypothetis_chain = langchain.chains.LLMChain(
            prompt=hypothesis_prompt, llm=self.llm, verbose=True
        )

        # TODO: can input vars just be deducted from the prompt? What about plugins?
        self.input_variables = [
            "input",
            "chat_history",
            "episodic_memory",
            "declarative_memory",
            "agent_scratchpad",
        ]

    def load_agent(self):
        self.agent_manager = AgentManager(
            llm=self.llm,
            tools=self.mad_hatter.tools,
            verbose=self.settings.verbose,
        )  # TODO: load from plugins

        self.agent_executor = self.agent_manager.get_agent_executor(
            prefix_prompt=self.prefix_prompt,
            suffix_prompt=self.suffix_prompt,
            input_variables=self.input_variables,
            return_intermediate_steps=True,
        )

    # retrieve conversation memories (things user said in conversation)
    def recall_memories(
        self, text=None, embedding=None, collection=None, return_format=str
    ):
        # retrieve memories
        memory_vectors = self.memory[collection].similarity_search_with_score_by_vector(
            embedding, k=1000
        )
        log(memory_vectors)
        memory_texts = [m[0].page_content.replace("\n", ". ") for m in memory_vectors]

        # TODO: filter by metadata (e.g. questions --> answer)

        if return_format == str:
            memories_separator = "\n  - "
            memory_content = memories_separator + memories_separator.join(memory_texts)
        else:
            memory_content = memory_texts

        # TODO: take away duplicates
        # TODO: insert time information (e.g "two days ago") in episodic memories
        # TODO: insert sources in document memories

        if self.settings.verbose:
            log(memory_content)

        return memory_content

    def get_hyde_text_and_embedding(self, user_message):
        # HyDE text
        hyde_text = self.hypothetis_chain.run(user_message)
        if self.settings.verbose:
            log(hyde_text)

        # HyDE embedding
        hyde_embedding = self.embedder.embed_query(hyde_text)

        return hyde_text, hyde_embedding

    def __call__(self, user_message):
        if self.settings.verbose:
            log(user_message)

        hyde_text, hyde_embedding = self.get_hyde_text_and_embedding(user_message)

        # recall relevant memories (episodic)
        episodic_memory_content = self.recall_memories(
            collection="episodes", text=hyde_text, embedding=hyde_embedding
        )

        # recall relevant memories (declarative)
        declarative_memory_content = self.recall_memories(
            collection="documents", text=hyde_text, embedding=hyde_embedding
        )

        # reply with agent
        cat_message = self.agent_executor(
            {
                "input": user_message,
                "episodic_memory": episodic_memory_content,
                "declarative_memory": declarative_memory_content,
                "chat_history": self.history,
            }
        )

        if self.settings.verbose:
            log(cat_message)

        # update conversation history
        self.history += f"Human: {user_message}\n"
        self.history += f'AI: {cat_message["output"]}\n'

        # store user message in episodic memory
        # TODO: also embed HyDE style
        # TODO: vectorize and store conversation chunks (not raw dialog, but summarization)
        _ = self.memory["episodes"].add_texts(
            [user_message],
            [
                {
                    "source": "user",
                    "when": time.time(),
                    "text": user_message,
                }
            ],
        )
        self.vector_store.save_vector_store("episodes", self.memory["episodes"])

        # build data structure for output (response and why with memories)
        final_output = {
            "error": False,
            "content": cat_message["output"],
            "why": {
                **cat_message,
                "episodic_memory": episodic_memory_content,
                "declarative_memory": declarative_memory_content,  # TODO: add sources
            },
        }

        return final_output
