import time
import traceback
from typing import Union

import langchain
from cat.utils import log
from cat.db.database import get_db_session, create_db_and_tables
from cat.rabbit_hole import RabbitHole
from starlette.datastructures import UploadFile
from cat.mad_hatter.mad_hatter import MadHatter
from cat.memory.working_memory import WorkingMemory
from cat.memory.long_term_memory import LongTermMemory
from langchain.docstore.document import Document
from cat.looking_glass.agent_manager import AgentManager


# main class
class CheshireCat:
    def __init__(self, verbose=True):
        self.verbose = verbose

        # access to DB
        self.load_db()

        # bootstrap the cat!
        self.bootstrap()

        # queue of cat messages not directly related to last user input
        # i.e. finished uploading a file
        self.web_socket_notifications = []

    def bootstrap(self):
        """This method is called when the cat is instantiated and
        has to be called whenever LLM, embedder, agent or memory need to be reinstantiated
        (for example an LLM change at runtime)
        """

        self.load_plugins()
        self.load_natural_language()
        self.load_memory()

        # Agent manager instance (for reasoning)
        self.agent_manager = AgentManager(self)

        # Rabbit Hole Instance
        self.rabbit_hole = RabbitHole()

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
            template=self.mad_hatter.execute_hook("get_hypothetical_embedding_prompt"),
        )

        self.hypothetis_chain = langchain.chains.LLMChain(
            prompt=hypothesis_prompt, llm=self.llm, verbose=True
        )

        self.summarization_prompt = self.mad_hatter.execute_hook(
            "get_summarization_prompt"
        )

        # custom summarization chain
        self.summarization_chain = langchain.chains.LLMChain(
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

    def load_memory(self):
        # Memory
        vector_memory_config = {"embedder": self.embedder, "verbose": True}
        self.memory = LongTermMemory(vector_memory_config=vector_memory_config)
        self.working_memory = WorkingMemory()

    def load_plugins(self):
        # Load plugin system
        self.mad_hatter = MadHatter(self)

    def get_hyde_text_and_embedding(self, text):
        # HyDE text
        hyde_text = self.hypothetis_chain.run(text)
        if self.verbose:
            log(hyde_text)

        # HyDE embedding
        hyde_embedding = self.embedder.embed_query(hyde_text)

        return hyde_text, hyde_embedding

    # iterative summarization
    def get_summary_text(self, docs, group_size=3):
        # service variable to store intermediate results
        intermediate_summaries = docs

        # we will store iterative summaries all together in a list
        all_summaries = []

        # loop until there are no groups to summarize
        root_summary_flag = False
        separator = "\n --> "
        while not root_summary_flag:
            # make summaries of groups of docs
            new_summaries = []
            for i in range(0, len(intermediate_summaries), group_size):
                group = intermediate_summaries[i : i + group_size]
                group = list(map(lambda d: d.page_content, group))

                summary = self.summarization_chain.run(
                    separator + separator.join(group)
                )
                summary = Document(page_content=summary)
                new_summaries.append(summary)

            # update list of all summaries
            all_summaries = new_summaries.copy() + all_summaries
            intermediate_summaries = new_summaries

            # did we reach root summary?
            root_summary_flag = len(intermediate_summaries) == 1

            if self.verbose:
                log(
                    f"Building summaries over {len(intermediate_summaries)} chunks. Please wait."
                )

        log(all_summaries)

        # return root summary and all intermediate summaries
        return all_summaries[0], all_summaries[1:]

    def send_file_in_rabbit_hole(
        self,
        file: Union[str, UploadFile],
        chunk_size: int = 400,
        chunk_overlap: int = 100,
    ):
        """
        Load a given file in the Cat's memory.

        :param file: absolute path of the file or UploadFile if ingested from the GUI
        :param chunk_size: number of characters the text is split in
        :param chunk_overlap: number of overlapping characters between consecutive chunks
        """

        # split file into a list of docs
        docs = RabbitHole.file_to_docs(
            file=file, chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

        # get summaries
        summary, intermediate_summaries = self.get_summary_text(docs)
        docs = [summary] + intermediate_summaries + docs

        # store in memory
        if isinstance(file, str):
            filename = file
        else:
            filename = file.filename
        RabbitHole.store_documents(ccat=self, docs=docs, source=filename)

    def send_url_in_rabbit_hole(
        self,
        url: str,
        chunk_size: int = 400,
        chunk_overlap: int = 100,
    ):
        """
        Load a given website in the Cat's memory.
        :param url: URL of the website to which you want to save the content
        :param chunk_size: number of characters the text is split in
        :param chunk_overlap: number of overlapping characters between consecutive chunks
        """

        # get website content and split into a list of docs
        docs = RabbitHole.url_to_docs(
            url=url, chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

        # get summaries and store
        summary, intermediate_summaries = self.get_summary_text(docs)
        docs = [summary] + intermediate_summaries + docs
        RabbitHole.store_documents(ccat=self, docs=docs, source=url)

    def recall_relevant_memories_to_working_memory(self, user_message):
        # TODO: should we compress convo history for better retrieval?

        # HyDE
        hyde_text, hyde_embedding = self.get_hyde_text_and_embedding(user_message)

        # recall relevant memories (episodic)
        episodic_memories = self.memory.vectors.episodic.recall_memories_from_embedding(
            embedding=hyde_embedding
        )
        self.working_memory["episodic_memories"] = episodic_memories

        # recall relevant memories (declarative)
        declarative_memories = (
            self.memory.vectors.declarative.recall_memories_from_embedding(
                embedding=hyde_embedding
            )
        )
        self.working_memory["declarative_memories"] = declarative_memories

    def __call__(self, user_message):
        if self.verbose:
            log(user_message)

        # recall episodic and declarative memories from vector collections and store them in working_memory
        try:
            self.recall_relevant_memories_to_working_memory(user_message)
        except Exception as e:
            log(e)
            traceback.print_exc(e)
            return {
                "error": False,
                # TODO: Otherwise the frontend gives notice of the error but does not show what the error is
                "content": "Vector memory error: you probably changed Embedder and old vector memory is not compatible. Please delete `core/long_term_memory` folder",
                "why": {},
            }

        # format memories to be inserted in the prompt
        episodic_memory_formatted_content = self.mad_hatter.execute_hook(
            "format_episodic_memories_for_prompt",
            self.working_memory["episodic_memories"],
        )
        declarative_memory_formatted_content = self.mad_hatter.execute_hook(
            "format_declarative_memories_for_prompt",
            self.working_memory["declarative_memories"],
        )

        # format conversation history to be inserted in the prompt
        conversation_history_formatted_content = self.mad_hatter.execute_hook(
            "format_conversation_history_for_prompt", self.working_memory["history"]
        )

        # load agent (will rebuild both agent and agent_executor based on context and plugins)
        agent_executor = self.agent_manager.get_agent_executor()

        # reply with agent
        try:
            cat_message = agent_executor(
                {
                    "input": user_message,
                    "episodic_memory": episodic_memory_formatted_content,
                    "declarative_memory": declarative_memory_formatted_content,
                    "chat_history": conversation_history_formatted_content,
                    "ai_prefix": "AI",
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
        self.working_memory.update_conversation_history(
            who="Human", message=user_message
        )
        self.working_memory.update_conversation_history(
            who="AI", message=cat_message["output"]
        )

        # store user message in episodic memory
        # TODO: vectorize and store also conversation chunks (not raw dialog, but summarization)
        _ = self.memory.vectors.episodic.add_texts(
            [user_message],
            [{"source": "user", "when": time.time()}],
        )

        # build data structure for output (response and why with memories)
        final_output = {
            "error": False,
            "content": cat_message["output"],
            "why": {
                "input": cat_message["input"],
                "output": cat_message["output"],
                "intermediate_steps": cat_message["intermediate_steps"],
                "memory": {
                    "vectors": {
                        "episodic": [
                            dict(d[0]) | {"score": float(d[1])}
                            for d in self.working_memory["episodic_memories"]
                        ],
                        "declarative": [
                            dict(d[0]) | {"score": float(d[1])}
                            for d in self.working_memory["declarative_memories"]
                        ],
                    }
                },
            },
        }

        final_output = self.mad_hatter.execute_hook(
            "before_returning_response_to_user", final_output
        )

        return final_output
