import json
import traceback
import random
from typing import List, Dict, Union
from copy import deepcopy

from langchain.agents import AgentExecutor
from langchain.prompts import ChatPromptTemplate
from langchain_core.prompts.chat import SystemMessagePromptTemplate
from langchain_core.runnables import RunnableConfig, RunnablePassthrough, RunnableLambda

from cat.agents.base_agent import BaseAgent, AgentOutput
from cat.looking_glass import prompts
from cat.looking_glass.output_parser import ChooseProcedureOutputParser
from cat.experimental.form import CatForm, CatFormState
from cat.mad_hatter.decorators.tool import CatTool
from cat.mad_hatter.mad_hatter import MadHatter
from cat.mad_hatter.plugin import Plugin
from cat.log import log
from cat.looking_glass.callbacks import ModelInteractionHandler


"""
Agent API:

.execute(stray) -> {
    "return_direct": bool,  # if True, the agent maanger will return the output directly and block chains
    "intermediate_steps": List[Tuple[Tuple[Tool, ToolInput], str]]  # list of intermediate steps executed
}


"""

class ProceduresAgent(BaseAgent):

    async def execute(self, stray) -> AgentOutput:
        
        # Run active form if present
        form_result = await self.execute_form_agent(stray)
        if form_result:
            return AgentOutput(**form_result)  # exit agent with form output

        # Select and run useful procedures
        intermediate_steps = []
        procedural_memories = stray.working_memory.procedural_memories
        if len(procedural_memories) > 0:
            log.debug(f"Procedural memories retrived: {len(procedural_memories)}.")

            try:
                procedures_result = await self.execute_procedures_agent(stray)
                if procedures_result.get("return_direct"):
                    # exit agent if a return_direct procedure was executed
                    return AgentOutput(**procedures_result)

                # store intermediate steps to enrich memory chain
                intermediate_steps = procedures_result["intermediate_steps"]

                # Adding the tools_output key in agent input, needed by the memory chain
                if len(intermediate_steps) > 0:
                    stray.working_memory.agent_input.tools_output = "## Context of executed system tools: \n"
                    for proc_res in intermediate_steps:
                        # ((step[0].tool, step[0].tool_input), step[1])
                        stray.working_memory.agent_input.tools_output += (
                            f" - {proc_res[0][0]}: {proc_res[1]}\n"
                        )

            except Exception as e:
                log.error(e)
                traceback.print_exc()

        return AgentOutput(
            output="",
            intermediate_steps=intermediate_steps,
            return_direct=False
        )

    async def execute_form_agent(self, stray):
        active_form = stray.working_memory.active_form
        if active_form:
            # closing form if state is closed
            if active_form._state == CatFormState.CLOSED:
                stray.working_memory.active_form = None
            else:
                # continue form
                form_out = active_form.next()
                # we assume for has always `return_direct` == True
                # TODO: this should be inserted in CatForm so devs can decide if the form jumps over memory
                form_out["return_direct"] = True
                return form_out

        return None  # no active form
    
    async def execute_procedures_agent(self, stray):

        # using some hooks
        mad_hatter = MadHatter()

        # Gather recalled procedures
        recalled_procedures_names = self.get_recalled_procedures_names(stray)
        recalled_procedures_names = mad_hatter.execute_hook(
            "agent_allowed_tools", recalled_procedures_names, cat=stray
        )

        # Prepare allowed procedures
        allowed_procedures, allowed_tools, return_direct_tools = (
            self.prepare_allowed_procedures(stray, recalled_procedures_names)
        )

        # Generate the prompt
        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(
                    template=mad_hatter.execute_hook(
                        "agent_prompt_instructions", prompts.TOOL_PROMPT, cat=stray
                    )
                ),
                # *(stray.langchainfy_chat_history())
            ]
        )

        # Partial the prompt with relevant data
        prompt = prompt.partial(
            tools="\n".join(
                f'- "{tool.name}": {tool.description}'
                for tool in allowed_procedures.values()
            ),
            tool_names='"' + '", "'.join(allowed_procedures.keys()) + '"',
            agent_scratchpad="",
            chat_history=stray.stringify_chat_history(),
            examples=self.generate_examples(allowed_procedures),
        )

        # Create the agent
        agent = (
            RunnablePassthrough.assign(
                agent_scratchpad=lambda x: self.generate_scratchpad(x["intermediate_steps"])
            )
            | prompt
            | RunnableLambda(lambda x: self._log_prompt(x, "TOOL PROMPT"))
            | stray._llm
            | RunnableLambda(lambda x: self._log_output(x, "TOOL PROMPT OUTPUT"))
            | ChooseProcedureOutputParser()
        )

        # Agent executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=allowed_tools,
            return_intermediate_steps=True,
            verbose=False,
            max_iterations=5,
        )

        # Agent run
        out = agent_executor.invoke(
            # convert to dict before passing to langchain
            # TODO: ensure dict keys and prompt placeholders map, so there are no issues on mismatches
            stray.working_memory.agent_input.model_dump(),
            config=RunnableConfig(callbacks=[ModelInteractionHandler(stray, self.__class__.__name__)])
        )

        # Process intermediate steps and handle forms
        out = self.process_intermediate_steps(stray, out, return_direct_tools, allowed_procedures)

        return out
    
    def get_recalled_procedures_names(self, stray):
        recalled_procedures_names = set()
        for p in stray.working_memory.procedural_memories:
            p_type = p[0].metadata["type"]
            p_trigger_type = p[0].metadata["trigger_type"]
            p_source = p[0].metadata["source"]
            if p_type in ["tool", "form"] \
                and p_trigger_type in ["description", "start_example"]:
                recalled_procedures_names.add(p_source)
        return recalled_procedures_names
    
    def prepare_allowed_procedures(self, stray, recalled_procedures_names):
        allowed_procedures: Dict[str, Union[CatTool, CatForm]] = {}
        allowed_tools: List[CatTool] = []
        return_direct_tools: List[str] = []

        mad_hatter = MadHatter()
        for p in mad_hatter.procedures:
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
    
    def generate_examples(self, allowed_procedures):
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
    
    def generate_scratchpad(self, intermediate_steps):
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += f"```json\n{action.log}\n```\n"
            thoughts += f"""```json
            {json.dumps({"action_output": observation}, indent=4)}
            ```
            """
        return thoughts
    
    def process_intermediate_steps(
        self,
        stray,
        out,
        return_direct_tools: List[str],
        allowed_procedures: Dict[str, Union[CatTool, CatForm]],
    ):
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