import time

import langchain
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from cat.db.database import get_db_session, create_db_and_tables
from cat.looking_glass.agent_manager import AgentManager
from cat.mad_hatter.mad_hatter import MadHatter
from cat.memory import VectorStore, VectorMemoryConfig
from cat.utils import log


# main class
class CheshireCat:
    def __init__(self, verbose=True):
        self.verbose = verbose

        # bootstrap the cat!
        self.load_db()
        self.load_plugins()
        self.load_agent()

    def load_db(self):
        # if there is no db, create it
        create_db_and_tables()

        db_session = get_db_session()

        # if there is no chosen LLM / EMBEDDER, set default ones
        # if there is a chosen non-default LLM / EMBEDDER, instantiate them

        # access db from instance
        self.db_session = db_session

    def load_plugins(self):
        # recent conversation # TODO: load from episodic memory latest conversation messages
        self.history = ""

        # Load plugin system
        self.mad_hatter = MadHatter()

        # LLM and embedder
        self.llm = self.mad_hatter.execute_hook("get_language_model", self)
        self.embedder = self.mad_hatter.execute_hook("get_language_embedder", self)

        # Prompts
        self.prefix_prompt = self.mad_hatter.execute_hook("get_main_prompt_prefix")
        self.suffix_prompt = self.mad_hatter.execute_hook("get_main_prompt_suffix")

        # Memory
        self.vector_store = VectorStore(VectorMemoryConfig(verbose=self.verbose))
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

        
        # TODO: we could import this from plugins
        self.summarization_prompt = """Write a concise summary of the following:
{text}
"""
        # TODO: import chain_type from settings
        self.summarization_chain = load_summarize_chain(
            self.llm, chain_type="stuff",
            prompt=langchain.PromptTemplate(
                template=self.summarization_prompt, input_variables=["text"]
            )
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
            verbose=self.verbose,
        )  # TODO: load agent from plugins? It's gonna be a MESS

        self.agent_executor = self.agent_manager.get_agent_executor(
            prefix_prompt=self.prefix_prompt,
            suffix_prompt=self.suffix_prompt,
            # ai_prefix="AI",
            # human_prefix="Human",
            input_variables=self.input_variables,
            return_intermediate_steps=True,
        )

    # retrieve similar memories from text
    def recall_memories_from_text(self, text=None, collection=None, metadata={}, k=5):
        # retrieve memories
        memories = self.memory[collection].similarity_search_with_score(query=text, k=k)

        # TODO: filter by metadata
        # With FAISS we need to first recall a lot of vectors from memory and filter afterwards.
        # With Qdrant we can use filters directly in the query

        return memories

    # retrieve similar memories from embedding
    def recall_memories_from_embedding(
        self, embedding=None, collection=None, metadata={}, k=5
    ):
        # recall from memory
        memories = self.memory[collection].similarity_search_with_score_by_vector(
            embedding=embedding, k=k
        )

        # TODO: filter by metadata
        # With FAISS we need to first recall a lot of vectors from memory and filter afterwards.
        # With Qdrant we can use filters directly in the query

        return memories

    # TODO: this should be a hook
    def format_memories_for_prompt(self, memory_docs, return_format=str):
        memory_texts = [m[0].page_content.replace("\n", ". ") for m in memory_docs]

        # TODO: take away duplicates
        # TODO: insert time information (e.g "two days ago") in episodic memories
        # TODO: insert sources in document memories

        if return_format == str:
            memories_separator = "\n  - "
            memory_content = memories_separator + memories_separator.join(memory_texts)
        else:
            memory_content = memory_texts

        if self.verbose:
            log(memory_content)

        return memory_content

    def get_hyde_text_and_embedding(self, text):
        # HyDE text
        hyde_text = self.hypothetis_chain.run(text)
        if self.verbose:
            log(hyde_text)

        # HyDE embedding
        hyde_embedding = self.embedder.embed_query(hyde_text)

        return hyde_text, hyde_embedding

    def get_summary_text(self, docs, group_size=3):
        flag = False
        while not flag:
            # TODO: should we save intermediate results?
            docs = [self.summarization_chain.run(docs[i:i+group_size]) for i in range(0,len(docs), group_size)]
            docs = [Document(page_content=doc) for doc in docs]
            flag = len(docs)==1

        if self.verbose:
            log(docs[0])
        return docs[0]

    def __call__(self, user_message):
        if self.verbose:
            log(user_message)

        hyde_text, hyde_embedding = self.get_hyde_text_and_embedding(user_message)

        # recall relevant memories (episodic)
        episodic_memory_content = self.recall_memories_from_embedding(
            embedding=hyde_embedding, collection="episodes"
        )
        episodic_memory_formatted_content = self.format_memories_for_prompt(
            episodic_memory_content
        )

        # recall relevant memories (declarative)
        declarative_memory_content = self.recall_memories_from_embedding(
            embedding=hyde_embedding, collection="documents"
        )
        declarative_memory_formatted_content = self.format_memories_for_prompt(
            declarative_memory_content
        )

        # reply with agent
        cat_message = self.agent_executor(
            {
                "input": user_message,
                "episodic_memory": episodic_memory_formatted_content,
                "declarative_memory": declarative_memory_formatted_content,
                "chat_history": self.history,
            }
        )

        if self.verbose:
            log(cat_message)

        # update conversation history
        self.history += f"Human: {user_message}\n"
        self.history += f'AI: {cat_message["output"]}\n'

        # store user message in episodic memory
        # TODO: vectorize and store also conversation chunks (not raw dialog, but summarization)
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
                "episodic_memory": [
                    dict(d[0]) | {"score": float(d[1])} for d in episodic_memory_content
                ],
                "declarative_memory": [
                    dict(d[0]) | {"score": float(d[1])}
                    for d in declarative_memory_content
                ],
            },
        }

        return final_output
