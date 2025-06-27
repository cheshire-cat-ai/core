import time
from typing import List, Tuple
from datetime import timedelta

from langchain.docstore.document import Document

from cat.mad_hatter.mad_hatter import MadHatter
from cat.looking_glass import prompts
from cat.utils import verbal_timedelta, BaseModelDict
from cat.env import get_env
from cat.agents import BaseAgent, AgentOutput
from cat.agents.memory_agent import MemoryAgent
from cat.agents.procedures_agent import ProceduresAgent


class MainAgent(BaseAgent):
    """Main Agent.
    This class manages sub agents that in turn use the LLM.
    """

    def __init__(self):
        self.mad_hatter = MadHatter()

        if get_env("CCAT_LOG_LEVEL") in ["DEBUG", "INFO"]:
            self.verbose = True
        else:
            self.verbose = False

    def execute(self, cat) -> AgentOutput:
        """Execute the agents.

        Returns
        -------
        agent_output : AgentOutput
            Reply of the agent, instance of AgentOutput.
        """

        # prepare input to be passed to the agent.
        #   Info will be extracted from working memory
        # Note: agent_input works both as a dict and as an object
        agent_input : BaseModelDict = self.format_agent_input(cat)
        agent_input = self.mad_hatter.execute_hook(
            "before_agent_starts", agent_input, cat=cat
        )

        # store the agent input inside the working memory
        cat.working_memory.agent_input = agent_input

        # should we run the default agents?
        agent_fast_reply = self.mad_hatter.execute_hook(
            "agent_fast_reply", {}, cat=cat
        )
        if isinstance(agent_fast_reply, AgentOutput):
            return agent_fast_reply
        if isinstance(agent_fast_reply, dict) and "output" in agent_fast_reply:
            return AgentOutput(**agent_fast_reply)

        # obtain prompt parts from plugins
        prompt_prefix = self.mad_hatter.execute_hook(
            "agent_prompt_prefix", prompts.MAIN_PROMPT_PREFIX, cat=cat
        )
        prompt_suffix = self.mad_hatter.execute_hook(
            "agent_prompt_suffix", prompts.MAIN_PROMPT_SUFFIX, cat=cat
        )

        # run tools and forms
        procedures_agent = ProceduresAgent()
        procedures_agent_out : AgentOutput = procedures_agent.execute(cat)
        if procedures_agent_out.return_direct:
            return procedures_agent_out

        # we run memory agent if:
        # - no procedures were recalled or selected or
        # - procedures have all return_direct=False
        memory_agent = MemoryAgent()
        memory_agent_out : AgentOutput = memory_agent.execute(
            # TODO: should all agents only receive StrayCat?
            cat, prompt_prefix, prompt_suffix
        )

        memory_agent_out.intermediate_steps += procedures_agent_out.intermediate_steps

        return memory_agent_out

    def format_agent_input(self, cat):
        """Format the input for the Agent.

        The method formats the strings of recalled memories and chat history that will be provided to the Langchain
        Agent and inserted in the prompt.

        Returns
        -------
        BaseModelDict
            Formatted output to be parsed by the Agent executor. Works both as a dict and as an object.

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
        episodic_memory_formatted_content = self.agent_prompt_episodic_memories(
            cat.working_memory.episodic_memories
        )
        declarative_memory_formatted_content = self.agent_prompt_declarative_memories(
            cat.working_memory.declarative_memories
        )

        # format conversation history to be inserted in the prompt
        # TODOV2: take away
        conversation_history_formatted_content = cat.working_memory.stringify_chat_history()

        return BaseModelDict(**{
            "episodic_memory": episodic_memory_formatted_content,
            "declarative_memory": declarative_memory_formatted_content,
            "tools_output": "",
            "input": cat.working_memory.user_message_json.text,  # TODOV2: take away
            "chat_history": conversation_history_formatted_content, # TODOV2: take away
        })

    def agent_prompt_episodic_memories(
        self, memory_docs: List[Tuple[Document, float]]
    ) -> str:
        """Formats episodic memories to be inserted into the prompt.

        Parameters
        ----------
        memory_docs : List[Document]
            List of Langchain `Document` retrieved from the episodic memory.

        Returns
        -------
        memory_content : str
            String of retrieved context from the episodic memory.
        """

        # convert docs to simple text
        memory_texts = [m[0].page_content.replace("\n", ". ") for m in memory_docs]

        # add time information (e.g. "2 days ago")
        memory_timestamps = []
        for m in memory_docs:
            # Get Time information in the Document metadata
            timestamp = m[0].metadata["when"]

            # Get Current Time - Time when memory was stored
            delta = timedelta(seconds=(time.time() - timestamp))

            # Convert and Save timestamps to Verbal (e.g. "2 days ago")
            memory_timestamps.append(f" ({verbal_timedelta(delta)})")

        # Join Document text content with related temporal information
        memory_texts = [a + b for a, b in zip(memory_texts, memory_timestamps)]

        # Format the memories for the output
        memories_separator = "\n  - "
        memory_content = (
            "## Context of things the Human said in the past: "
            + memories_separator
            + memories_separator.join(memory_texts)
        )

        # if no data is retrieved from memory don't erite anithing in the prompt
        if len(memory_texts) == 0:
            memory_content = ""

        return memory_content

    def agent_prompt_declarative_memories(
        self, memory_docs: List[Tuple[Document, float]]
    ) -> str:
        """Formats the declarative memories for the prompt context.
        Such context is placed in the `agent_prompt_prefix` in the place held by {declarative_memory}.

        Parameters
        ----------
        memory_docs : List[Document]
            list of Langchain `Document` retrieved from the declarative memory.

        Returns
        -------
        memory_content : str
            String of retrieved context from the declarative memory.
        """

        # convert docs to simple text
        memory_texts = [m[0].page_content.replace("\n", ". ") for m in memory_docs]

        # add source information (e.g. "extracted from file.txt")
        memory_sources = []
        for m in memory_docs:
            # Get and save the source of the memory
            source = m[0].metadata["source"]
            memory_sources.append(f" (extracted from {source})")

        # Join Document text content with related source information
        memory_texts = [a + b for a, b in zip(memory_texts, memory_sources)]

        # Format the memories for the output
        memories_separator = "\n  - "

        memory_content = (
            "## Context of documents containing relevant information: "
            + memories_separator
            + memories_separator.join(memory_texts)
        )

        # if no data is retrieved from memory don't write anithing in the prompt
        if len(memory_texts) == 0:
            memory_content = ""

        return memory_content


