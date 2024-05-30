import os
import time
import json
import random
import traceback
from copy import deepcopy
from typing import List, Dict, Union, Tuple
from datetime import timedelta

from langchain_core.utils import get_colored_text
from langchain.agents import AgentExecutor
from langchain.docstore.document import Document
from langchain_core.output_parsers.string import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_core.prompts.chat import SystemMessagePromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain.callbacks.tracers import ConsoleCallbackHandler

from cat.mad_hatter.plugin import Plugin
from cat.mad_hatter.mad_hatter import MadHatter
from cat.mad_hatter.decorators.tool import CatTool
from cat.looking_glass import prompts
from cat.looking_glass.output_parser import ChooseProcedureOutputParser
from cat.utils import verbal_timedelta
from cat.log import log
from cat.env import get_env
from cat.looking_glass.callbacks import NewTokenHandler
from cat.experimental.form import CatForm, CatFormState


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

        if get_env("CCAT_LOG_LEVEL") in ["DEBUG", "INFO"]:
            self.verbose = True
        else:
            self.verbose = False


    async def execute_procedures_agent(self, agent_input, stray):
        
        def get_recalled_procedures_names():
            recalled_procedures_names = set()
            for p in stray.working_memory.procedural_memories:
                procedure = p[0]
                if procedure.metadata["type"] in ["tool", "form"] and procedure.metadata["trigger_type"] in ["description", "start_example"]:
                    recalled_procedures_names.add(procedure.metadata["source"])
            return recalled_procedures_names

        def prepare_allowed_procedures():
            allowed_procedures: Dict[str, Union[CatTool, CatForm]] = {}
            allowed_tools: List[CatTool] = []
            return_direct_tools: List[str] = []

            for p in self.mad_hatter.procedures:
                if p.name in recalled_procedures_names:
                    if Plugin._is_cat_tool(p):
                        tool = deepcopy(p)
                        tool.assign_cat(stray)
                        allowed_tools.append(tool)
                        allowed_procedures[tool.name] = tool
                        if p.return_direct:
                            return_direct_tools.append(tool.name)
                    else:
                        allowed_procedures[p.name] = p
            
            return allowed_procedures, allowed_tools, return_direct_tools

        def generate_examples():
            list_examples = ""
            for proc in allowed_procedures.values():
                if proc.start_examples:
                    if not list_examples:
                        list_examples += "## Here some examples:\n"
                    example_json = f"""
                    {{
                        "action": "{proc.name}",
                        "action_input": // Input of the action according to its description
                    }}"""
                    list_examples += f"\nQuestion: {random.choice(proc.start_examples)}"
                    list_examples += f"\n```json\n{example_json}\n```"
                    list_examples += """```json
                    {{
                        "action": "final_answer",
                        "action_input": null
                    }}
                    ```"""
            return list_examples

        def generate_scratchpad(intermediate_steps):
            thoughts = ""
            for action, observation in intermediate_steps:
                thoughts += f"```json\n{action.log}\n```\n"
                thoughts += f"""```json
                {json.dumps({"action_output": observation}, indent=4)}
                ```
                """
            return thoughts

        def process_intermediate_steps(out, return_direct_tools: List[str], allowed_procedures: Dict[str, Union[CatTool, CatForm]]):
            """
            Process intermediate steps and check if any tool is decorated with return_direct=True.
            Also, include forms in the intermediate steps and handle their selection.
            """
            out["return_direct"] = False
            intermediate_steps = []

            for step in out.get("intermediate_steps", []):
                intermediate_steps.append(((step[0].tool, step[0].tool_input), step[1]))
                if step[0].tool in return_direct_tools:
                    out["return_direct"] = True
            
            out["intermediate_steps"] = intermediate_steps

            if "form" in out:
                form_name = out["form"]
                if form_name in allowed_procedures:
                    FormClass = allowed_procedures[form_name]
                    form_instance = FormClass(stray)
                    stray.working_memory.active_form = form_instance
                    out = form_instance.next()
                    out["return_direct"] = True
                    intermediate_steps.append(((form_name, None), out["output"]))

            out["intermediate_steps"] = intermediate_steps
            return out

        # Gather recalled procedures
        recalled_procedures_names = get_recalled_procedures_names()
        recalled_procedures_names = self.mad_hatter.execute_hook("agent_allowed_tools", recalled_procedures_names, cat=stray)

        # Prepare allowed procedures
        allowed_procedures, allowed_tools, return_direct_tools = prepare_allowed_procedures()

        # Generate the prompt
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                template=self.mad_hatter.execute_hook("agent_prompt_instructions", prompts.TOOL_PROMPT, cat=stray)
            ),
            # *(stray.langchainfy_chat_history())
        ])

        # Partial the prompt with relevant data
        prompt = prompt.partial(
            tools="\n".join(f"- {tool.name}: {tool.description}" for tool in allowed_procedures.values()),
            tool_names=", ".join(allowed_procedures.keys()),
            agent_scratchpad="",
            chat_history=stray.stringify_chat_history(),
            examples=generate_examples(),
        )

        # Create the agent
        agent = (
            RunnablePassthrough.assign(
                agent_scratchpad=lambda x: generate_scratchpad(x["intermediate_steps"])
            )
            | prompt
            | RunnableLambda(lambda x: self.__log_prompt(x))
            | stray._llm
            | ChooseProcedureOutputParser()
        )

        # Agent executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=allowed_tools,
            return_intermediate_steps=True,
            verbose=True,
            max_iterations=5,
        )

        # Agent run
        out = agent_executor.invoke(agent_input)

        # Process intermediate steps and handle forms
        out = process_intermediate_steps(out, return_direct_tools, allowed_procedures)

        return out

    async def execute_form_agent(self, stray):
        active_form = stray.working_memory.active_form
        if active_form:
            # closing form if state is closed
            if active_form._state == CatFormState.CLOSED:
                stray.working_memory.active_form = None
            else:
                # continue form
                return active_form.next()

        return None  # no active form

    async def execute_memory_chain(
        self, agent_input, prompt_prefix, prompt_suffix, stray
    ):
        final_prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(
                    template=prompt_prefix + prompt_suffix
                ),
                *(stray.langchainfy_chat_history())
            ]
        )

        memory_chain = (
            final_prompt
            | RunnableLambda(lambda x: self.__log_prompt(x))
            | stray._llm
            | StrOutputParser()
        )

        agent_input["output"] = memory_chain.invoke(
            agent_input, 
            config=RunnableConfig(callbacks=[NewTokenHandler(stray)])
        )
        
        return agent_input

    async def execute_agent(self, stray):
        """Instantiate the Agent with tools.

        The method formats the main prompt and gather the allowed tools/forms. It also instantiates a conversational Agent
        from Langchain.

        Returns
        -------
        agent_executor : agent reply
            Reply of the Agent in the format `{"output": ..., "intermediate_steps": ...}`.
        """

        # prepare input to be passed to the agent.
        #   Info will be extracted from working memory
        agent_input = self.format_agent_input(stray)
        agent_input = self.mad_hatter.execute_hook(
            "before_agent_starts", agent_input, cat=stray
        )

        # should we run the default agent?
        fast_reply = {}
        fast_reply = self.mad_hatter.execute_hook(
            "agent_fast_reply", fast_reply, cat=stray
        )
        if len(fast_reply.keys()) > 0:
            return fast_reply

        # obtain prompt parts from plugins
        prompt_prefix = self.mad_hatter.execute_hook(
            "agent_prompt_prefix", prompts.MAIN_PROMPT_PREFIX, cat=stray
        )
        prompt_suffix = self.mad_hatter.execute_hook(
            "agent_prompt_suffix", prompts.MAIN_PROMPT_SUFFIX, cat=stray
        )

        # Run active form if present
        form_result = await self.execute_form_agent(stray)
        if form_result:
            return form_result  # exit agent with form output

        # Select and run useful procedures
        intermediate_steps = []
        procedural_memories = stray.working_memory.procedural_memories
        if len(procedural_memories) > 0:
            log.debug(f"Procedural memories retrived: {len(procedural_memories)}.")

            try:
                procedures_result = await self.execute_procedures_agent(
                    agent_input, stray
                )
                if procedures_result.get("return_direct"):
                    # exit agent if a return_direct procedure was executed
                    return procedures_result

                # store intermediate steps to enrich memory chain
                intermediate_steps = procedures_result["intermediate_steps"]

                # Adding the tools_output key in agent input, needed by the memory chain
                if len(intermediate_steps) > 0:
                    agent_input["tools_output"] = "## Tools output: \n"
                    for proc_res in intermediate_steps:
                        # ((step[0].tool, step[0].tool_input), step[1])
                        agent_input["tools_output"] += (
                            f" - {proc_res[0][0]}: {proc_res[1]}\n"
                        )

            except Exception as e:
                log.error(e)
                traceback.print_exc()

        # we run memory chain if:
        # - no procedures where recalled or selected or
        # - procedures have all return_direct=False or
        # - procedures agent crashed big time

        memory_chain_output = await self.execute_memory_chain(
            agent_input, prompt_prefix, prompt_suffix, stray
        )
        memory_chain_output["intermediate_steps"] = intermediate_steps

        return memory_chain_output

    def format_agent_input(self, stray):
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
            stray.working_memory.episodic_memories
        )
        declarative_memory_formatted_content = self.agent_prompt_declarative_memories(
            stray.working_memory.declarative_memories
        )

        # format conversation history to be inserted in the prompt
        #conversation_history_formatted_content = stray.stringify_chat_history()

        return {
            "input": stray.working_memory.user_message_json.text,  # TODO: deprecate, since it is included in chat history
            "episodic_memory": episodic_memory_formatted_content,
            "declarative_memory": declarative_memory_formatted_content,
            #"chat_history": conversation_history_formatted_content,
            "tools_output": "",
        }

    def agent_prompt_episodic_memories(self, memory_docs: List[Tuple[Document, float]]) -> str:
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

    def agent_prompt_declarative_memories(self, memory_docs: List[Tuple[Document, float]]) -> str:
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

    def __log_prompt(self, x):
            #The names are not shown in the chat history log, the model however receives the name correctly
            log.info("The names are not shown in the chat history log, the model however receives the name correctly")            
            print("\n",get_colored_text(x.to_string(),"green"))
            return x