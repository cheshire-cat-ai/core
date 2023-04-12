import time
from typing import Union

import langchain
from cat.utils import log
from cat.memory import VectorStore, VectorMemoryConfig
from cat.db.database import get_db_session, create_db_and_tables
from cat.mad_hatter.mad_hatter import MadHatter
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from cat.looking_glass.agent_manager import AgentManager
from cat.rabbit_hole import RabbitHole
from fastapi import UploadFile


# main class
class CheshireCat:
    def __init__(self, verbose=True):
        self.verbose = verbose

        # bootstrap the cat!
        self.bootstrap()

        # Rabbit Hole Instance
        self.rabbit_hole = RabbitHole()

    def bootstrap(self):
        """This method is called when the cat is instantiated and
        has to be called whenever LLM, embedder, agent or memory need to be reinstantiated
        (for example an LLM change at runtime)
        """
        self.load_db()
        self.load_plugins()
        self.load_agent()

    def load_db(self):
        # if there is no db, create it
        create_db_and_tables()

        db_session = get_db_session()

        # access db from instance
        self.db_session = db_session

    def load_plugins(self):
        # recent conversation # TODO: load from episodic memory latest conversation messages
        self.history = ""

        # Load plugin system
        self.mad_hatter = MadHatter(self)

        # LLM and embedder
        self.llm = self.mad_hatter.execute_hook("get_language_model")
        self.embedder = self.mad_hatter.execute_hook("get_language_embedder")

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
            self.llm,
            chain_type="stuff",
            prompt=langchain.PromptTemplate(
                template=self.summarization_prompt, input_variables=["text"]
            ),
        )

        # custom summarization chain
        self.custom_summarization_chain = langchain.chains.LLMChain(
            llm=self.llm,
            verbose=False,
            prompt=langchain.PromptTemplate(
                template=self.summarization_prompt, input_variables=["text"]
            ),
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

    # iterative summarization
    def get_summary_text(self, docs, group_size=3, custom=True):
        # service variable to store intermediate results
        intermediate_summaries = docs

        # we will store iterative summaries all together in a list
        all_summaries = []

        summarization_chain = (
            self.custom_summarization_chain if custom else self.summarization_chain
        )

        # loop until there are no groups to summarize
        root_summary_flag = False
        while not root_summary_flag:
            # make summaries of groups of docs
            intermediate_summaries = [
                summarization_chain.run(intermediate_summaries[i: i + group_size])
                for i in range(0, len(intermediate_summaries), group_size)
            ]
            intermediate_summaries = [
                Document(page_content=summary) for summary in intermediate_summaries
            ]

            # update list of all summaries
            all_summaries = intermediate_summaries + all_summaries

            # did we reach root summary?
            root_summary_flag = len(intermediate_summaries) == 1

            if self.verbose:
                log(
                    f"Building summaries over {len(intermediate_summaries)} chunks. Please wait."
                )

        # return root summary and all intermediate summaries
        return all_summaries[0], all_summaries[1:]

    def send_file_in_rabbit_hole(
            self,
            file: Union[str, UploadFile],
            chunk_size: int = 400,
            chunk_overlap: int = 100
    ):
        """
        Load a given file in the Cat's memory.

        :param file: absolute path of the file or UploadFile if ingested from the GUI
        :param chunk_size: number of characters the text is split in
        :param chunk_overlap: number of overlapping characters between consecutive chunks
        """

        # Load the file in the cat memory
        self.rabbit_hole.ingest_file(self,
                                     file=file,
                                     chunk_size=chunk_size,
                                     chunk_overlap=chunk_overlap)

    def __call__(self, user_message):
        if self.verbose:
            log(user_message)

        hyde_text, hyde_embedding = self.get_hyde_text_and_embedding(user_message)

        try:
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
        except Exception:
            return {
                "error": False,
                # TODO: Otherwise the frontend gives notice of the error but does not show what the error is
                "content": "Vector memory error: you probably changed Embedder and old vector memory is not compatible. Please delete `web/long_term_memory` folder",
                "why": {},
            }

        # reply with agent
        try:
            cat_message = self.agent_executor(
                {
                    "input": user_message,
                    "episodic_memory": episodic_memory_formatted_content,
                    "declarative_memory": declarative_memory_formatted_content,
                    "chat_history": self.history,
                }
            )
        except ValueError as e:
            # This error happens when the LLM does not respect prompt instructions.
            # We grab the LLM outptu here anyway, so small and non instruction-fine-tuned models can still be used.
            error_description = str(e)
            if not error_description.startswith("Could not parse LLM output: `"):
                raise e

            unparsable_llm_output = error_description.removeprefix(
                "Could not parse LLM output: `"
            ).removesuffix("`")
            cat_message = {"output": unparsable_llm_output}

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
