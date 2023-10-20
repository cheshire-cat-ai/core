import time
import traceback
from datetime import timedelta
from typing import List, Dict

from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.agents import AgentExecutor, LLMSingleActionAgent

from cat.looking_glass import prompts
from cat.looking_glass.callbacks import NewTokenHandler
from cat.looking_glass.output_parser import ToolOutputParser
from cat.utils import verbal_timedelta
from cat.log import log


class AgentManager:
    """Manager of Langchain Agent.

    This class manages the Agent that uses the LLM. It takes care of formatting the prompt and filtering the tools
    before feeding them to the Agent. It also instantiates the Langchain Agent.

    Attributes
    ----------
    cat : CheshireCat
        Cheshire Cat instance.

    """
    def __init__(self, cat):
        self.cat = cat


    def execute_tool_agent(self, agent_input, allowed_tools):

        allowed_tools_names = [t.name for t in allowed_tools]
        # TODO: dynamic input_variables as in the main prompt 

        prompt = prompts.ToolPromptTemplate(
            template = self.cat.mad_hatter.execute_hook("agent_prompt_instructions", prompts.TOOL_PROMPT),
            tools=allowed_tools,
            # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
            # This includes the `intermediate_steps` variable because it is needed to fill the scratchpad
            input_variables=["input", "intermediate_steps"]
        )

        # main chain
        agent_chain = LLMChain(
            prompt=prompt,
            llm=self.cat._llm,
            verbose=True
        )

        # init agent
        agent = LLMSingleActionAgent(
            llm_chain=agent_chain,
            output_parser=ToolOutputParser(),
            stop=["\nObservation:"],
            allowed_tools=allowed_tools_names,
            verbose=True
        )

        # agent executor
        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=allowed_tools,
            return_intermediate_steps=True,
            verbose=True
        )

        out = agent_executor(agent_input)
        return out
    

    def execute_memory_chain(self, agent_input, prompt_prefix, prompt_suffix):

        input_variables = [i for i in agent_input.keys() if i in prompt_prefix + prompt_suffix]
        
        # memory chain (second step)
        memory_prompt = PromptTemplate(
            template = prompt_prefix + prompt_suffix,
            input_variables=input_variables
        )

        memory_chain = LLMChain(
            prompt=memory_prompt,
            llm=self.cat._llm,
            verbose=True
        )

        out = memory_chain(agent_input, callbacks=[NewTokenHandler(self.cat)])
        out["output"] = out["text"]
        del out["text"]
        return out


    def execute_agent(self):
        """Instantiate the Agent with tools.

        The method formats the main prompt and gather the allowed tools. It also instantiates a conversational Agent
        from Langchain.

        Returns
        -------
        agent_executor : AgentExecutor
            Instance of the Agent provided with a set of tools.
        """
        mad_hatter = self.cat.mad_hatter
        working_memory = self.cat.working_memory

        # prepare input to be passed to the agent.
        #   Info will be extracted from working memory
        agent_input = self.format_agent_input()
        agent_input = mad_hatter.execute_hook("before_agent_starts", agent_input)
        # should we ran the default agent?
        fast_reply = {}
        fast_reply = mad_hatter.execute_hook("agent_fast_reply", fast_reply)
        if len(fast_reply.keys()) > 0:
            return fast_reply
        prompt_prefix = mad_hatter.execute_hook("agent_prompt_prefix", prompts.MAIN_PROMPT_PREFIX)
        prompt_suffix = mad_hatter.execute_hook("agent_prompt_suffix", prompts.MAIN_PROMPT_SUFFIX)


        # tools currently recalled in working memory
        recalled_tools = working_memory["procedural_memories"]
        # Get the tools names only
        tools_names = [t[0].metadata["name"] for t in recalled_tools]
        tools_names = mad_hatter.execute_hook("agent_allowed_tools", tools_names)
        # Get tools with that name from mad_hatter
        allowed_tools = [i for i in mad_hatter.tools if i.name in tools_names]

        # Try to get information from tools if there is some allowed
        if len(allowed_tools) > 0:

            log.debug(f"{len(allowed_tools)} allowed tools retrived.")

            try:
                tools_result = self.execute_tool_agent(agent_input, allowed_tools)

                # If tools_result["output"] is None the LLM has used the fake tool none_of_the_others  
                # so no relevant information has been obtained from the tools.
                if tools_result["output"] != None:
                    
                    # Extract of intermediate steps in the format ((tool_name, tool_input), output)
                    used_tools = list(map(lambda x:((x[0].tool, x[0].tool_input), x[1]), tools_result["intermediate_steps"]))

                    # Get the name of the tools that have return_direct
                    return_direct_tools = []
                    for t in allowed_tools:
                        if t.return_direct:
                            return_direct_tools.append(t.name)

                    # execute_tool_agent returns immediately when a tool with return_direct is called, 
                    # so if one is used it is definitely the last one used
                    if used_tools[-1][0][0] in return_direct_tools:
                        # intermediate_steps still contains the information of all the tools used even if their output is not returned
                        tools_result["intermediate_steps"] = used_tools
                        return tools_result

                    #Adding the tools_output key in agent input, needed by the memory chain
                    agent_input["tools_output"] = "## Tools output: \n" + tools_result["output"] if tools_result["output"] else ""

                    # Execute the memory chain
                    out = self.execute_memory_chain(agent_input, prompt_prefix, prompt_suffix)

                    # If some tools are used the intermediate step are added to the agent output
                    out["intermediate_steps"] = used_tools

                    #Early return
                    return out

            except Exception as e:
                log.error(e)
                traceback.print_exc()

        #If an exeption occur in the execute_tool_agent or there is no allowed tools execute only the memory chain

        #Adding the tools_output key in agent input, needed by the memory chain
        agent_input["tools_output"] = ""
        # Execute the memory chain
        out = self.execute_memory_chain(agent_input, prompt_prefix, prompt_suffix)

        return out
    
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

        working_memory = self.cat.working_memory

        # format memories to be inserted in the prompt
        episodic_memory_formatted_content = self.agent_prompt_episodic_memories(
            working_memory["episodic_memories"]
        )
        declarative_memory_formatted_content = self.agent_prompt_declarative_memories(
            working_memory["declarative_memories"]
        )

        # format conversation history to be inserted in the prompt
        conversation_history_formatted_content = self.agent_prompt_chat_history(
            working_memory["history"]
        )

        return {
            "input": working_memory["user_message_json"]["text"],
            "episodic_memory": episodic_memory_formatted_content,
            "declarative_memory": declarative_memory_formatted_content,
            "chat_history": conversation_history_formatted_content,
        }

    def agent_prompt_episodic_memories(self, memory_docs: List[Document]) -> str:
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
        memory_content = "## Context of things the Human said in the past: " + \
            memories_separator + memories_separator.join(memory_texts)

        # if no data is retrieved from memory don't erite anithing in the prompt
        if len(memory_texts) == 0:
            memory_content = ""

        return memory_content

    def agent_prompt_declarative_memories(self, memory_docs: List[Document]) -> str:
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

        memory_content = "## Context of documents containing relevant information: " + \
            memories_separator + memories_separator.join(memory_texts)

        # if no data is retrieved from memory don't erite anithing in the prompt
        if len(memory_texts) == 0:
            memory_content = ""

        return memory_content

    def agent_prompt_chat_history(self, chat_history: List[Dict]) -> str:
        """Serialize chat history for the agent input.
        Converts to text the recent conversation turns fed to the *Agent*.

        Parameters
        ----------
        chat_history : List[Dict]
            List of dictionaries collecting speaking turns.

        Returns
        -------
        history : str
            String with recent conversation turns to be provided as context to the *Agent*.

        Notes
        -----
        Such context is placed in the `agent_prompt_suffix` in the place held by {chat_history}.

        The chat history is a dictionary with keys::
            'who': the name of who said the utterance;
            'message': the utterance.

        """
        history = ""
        for turn in chat_history:
            history += f"\n - {turn['who']}: {turn['message']}"

        return history

