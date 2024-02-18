import os
import time
import traceback
from datetime import timedelta
from typing import List, Dict

from copy import deepcopy

from langchain_core.runnables import RunnableConfig
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.agents import AgentExecutor, LLMSingleActionAgent

from cat.mad_hatter.plugin import Plugin
from cat.mad_hatter.mad_hatter import MadHatter
from cat.mad_hatter.decorators.tool import CatTool
from cat.looking_glass import prompts
from cat.looking_glass.callbacks import NewTokenHandler
from cat.looking_glass.output_parser import ToolOutputParser
from cat.utils import verbal_timedelta
from cat.log import log

from cat.experimental.form import CatForm


class AgentManager:
    """Manager of Langchain Agent.

    This class manages the Agent that uses the LLM. It takes care of formatting the prompt and filtering the tools
    before feeding them to the Agent. It also instantiates the Langchain Agent.

    Attributes
    ----------
    cat : CheshireCat
        Cheshire Cat instance.

    """
    def __init__(self):
        self.mad_hatter = MadHatter()

        if os.getenv("LOG_LEVEL", "INFO") in ["DEBUG", "INFO"]:
            self.verbose = True
        else:
            self.verbose = False

    async def execute_tool_agent(self, agent_input, stray):

        recalled_procedures_names = set()
        for p in stray.working_memory["procedural_memories"]:
            procedure = p[0]
            if procedure.metadata["source"] in ["tool", "tool_example", "form", "form_example"]:
                recalled_procedures_names.add(procedure.metadata["name"])

        log.critical(recalled_procedures_names)
            
        # tools currently recalled in working memory
        
        # Get tools with that name from mad_hatter
        allowed_procedures_names = []
        allowed_procedures = []
        allowed_tools = []
        for p in self.mad_hatter.procedures:
            if Plugin._is_cat_tool(p):
                if p.name in recalled_procedures_names:
                    # Prepare the tool to be used in the Cat (adding properties)
                    tool = deepcopy(p)
                    tool.assign_cat(stray)
                    allowed_tools.append(tool)
                    allowed_procedures.append(tool)
                    allowed_procedures_names.append(tool.name)
                    log.critical(f"Added: {p.name}")
            
            if Plugin._is_cat_form(p):
                if p.__name__ in recalled_procedures_names:
                    allowed_procedures.append(p)
                    allowed_procedures_names.append(p.__name__)
                    log.critical(f"Added: {p.__name__}")

        
        log.warning(allowed_procedures)

        #recalled_tools_names = self.mad_hatter.execute_hook("agent_allowed_tools", recalled_tools_names, cat=stray)

        # TODO: dynamic input_variables as in the main prompt 

        prompt = prompts.ToolPromptTemplate(
            template = self.mad_hatter.execute_hook("agent_prompt_instructions", prompts.TOOL_PROMPT, cat=stray),
            procedures=allowed_procedures,
            procedures_names=allowed_procedures_names,
            # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
            # This includes the `intermediate_steps` variable because it is needed to fill the scratchpad
            input_variables=["input", "intermediate_steps"]
        )

        # main chain
        agent_chain = LLMChain(
            prompt=prompt,
            llm=stray._llm,
            verbose=self.verbose
        )

        # init agent
        agent = LLMSingleActionAgent(
            llm_chain=agent_chain,
            output_parser=ToolOutputParser(),
            stop=["\nObservation:"],
            #allowed_tools=allowed_procedures_names,
            verbose=self.verbose
        )

        # agent executor
        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=allowed_tools,
            return_intermediate_steps=True,
            verbose=self.verbose
        )

        out = await agent_executor.ainvoke(agent_input)

        if "form" in out.keys():
            for Form in self.mad_hatter.forms:
                if Form.__name__ == out["form"]:
                    form = Form(stray)
                    stray.working_memory["forms"] = form
                    return {
                        "output": form.next(),
                        "intermediate_steps": []
                    }

        return out

    def execute_form_agent(self, agent_input, allowed_forms, stray):
        
        '''
        TODO:
        After vectorizing (in cheshire_cat.embed_procedures) to procedural memory the start 
        and stop of the catforms, and to episodic memory the catform examples ..

        1) Check working memory if there is an active form;
        
        2) if there is an active form, check from procedural memory whether 
           the form stop has been invoked;
        
        3) if the form stop has not been invoked, follow the dialogue,
           considering that if strict is False any tools must also be executed
           (classic memory chain with cform.dialog_action and cform.dialog_prompt);
        
        4) if there is no active form, check from procedural memory whether 
           start has been invoked of a form and if so start it.
        '''



        '''
        # Acquires the current form from working memory
        CURRENT_FORM_KEY = "CURRENT_FORM"
        if CURRENT_FORM_KEY in stray.working_memory:
            cat_form = stray.working_memory[CURRENT_FORM_KEY]
            
            if cat_form.strict is True:
                response = cat_form.dialogue_direct()
            else:
                #...

        return response
        '''
        return None
    
    async def execute_memory_chain(self, agent_input, prompt_prefix, prompt_suffix, stray):

        input_variables = [i for i in agent_input.keys() if i in prompt_prefix + prompt_suffix]
        # memory chain (second step)
        memory_prompt = PromptTemplate(
            template = prompt_prefix + prompt_suffix,
            input_variables=input_variables
        )

        memory_chain = LLMChain(
            prompt=memory_prompt,
            llm=stray._llm,
            verbose=self.verbose,
            output_key="output"
        )

        out = await memory_chain.ainvoke(agent_input, config=RunnableConfig(callbacks=[NewTokenHandler(stray)]))

        return out

    async def execute_agent(self, stray):
        """Instantiate the Agent with tools.

        The method formats the main prompt and gather the allowed tools. It also instantiates a conversational Agent
        from Langchain.

        Returns
        -------
        agent_executor : AgentExecutor
            Instance of the Agent provided with a set of tools.
        """

        # prepare input to be passed to the agent.
        #   Info will be extracted from working memory
        agent_input = self.format_agent_input(stray.working_memory)
        agent_input = self.mad_hatter.execute_hook("before_agent_starts", agent_input, cat=stray)
        # should we run the default agent?
        fast_reply = {}
        fast_reply = self.mad_hatter.execute_hook("agent_fast_reply", fast_reply, cat=stray)
        if len(fast_reply.keys()) > 0:
            return fast_reply
        prompt_prefix = self.mad_hatter.execute_hook("agent_prompt_prefix", prompts.MAIN_PROMPT_PREFIX, cat=stray)
        prompt_suffix = self.mad_hatter.execute_hook("agent_prompt_suffix", prompts.MAIN_PROMPT_SUFFIX, cat=stray)
        
        
        #################################
        # TODO: here we only deal with forms
        active_form = stray.working_memory.get("forms", None)
        if active_form:
            return {
                "output": active_form.next()
            }
        ############### TODO END

        # Try to get information from tools if there is some allowed
        procedural_memories = stray.working_memory["procedural_memories"]
        if len(procedural_memories) > 0:

            log.debug(f"Procedural memories retrived: {len(procedural_memories)}.")

            try:
                tools_result = await self.execute_tool_agent(agent_input, stray)

                #################################
                # TODO: here we only deal with forms
                active_form = stray.working_memory.get("forms", None)
                if active_form:
                    return {
                        "output": active_form.next()
                    }
                ############### TODO END

                # If tools_result["output"] is None the LLM has used the fake tool none_of_the_others  
                # so no relevant information has been obtained from the tools.
                if tools_result["output"] and tools_result["intermediate_steps"]:
                    # Extract of intermediate steps in the format ((tool_name, tool_input), output)
                    used_tools = list(map(lambda x:((x[0].tool, x[0].tool_input), x[1]), tools_result["intermediate_steps"]))

                    # Get the name of the tools that have return_direct
                    recalled_tools_names = set()
                    for p in stray.working_memory["procedural_memories"]:
                        procedure = p[0]
                        if procedure.metadata["source"] in ["tool", "tool_example"]:
                            recalled_tools_names.add(procedure.metadata["name"])
                    allowed_tools = [t for t in self.mad_hatter.tools if t.name in recalled_tools_names]
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
                    out = await self.execute_memory_chain(agent_input, prompt_prefix, prompt_suffix, stray)

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
        out = await self.execute_memory_chain(agent_input, prompt_prefix, prompt_suffix, stray)

        return out
    
    def format_agent_input(self, working_memory):
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

