import json
import traceback
import random
from typing import List, Dict, Union

from langchain.prompts import ChatPromptTemplate
from langchain_core.prompts.chat import SystemMessagePromptTemplate
from langchain_core.runnables import RunnableConfig, RunnablePassthrough, RunnableLambda

from cat.agents.base_agent import BaseAgent, AgentOutput
from cat.looking_glass import prompts
from cat.looking_glass.output_parser import ChooseProcedureOutputParser, LLMAction
from cat.experimental.form import CatForm, CatFormState
from cat.mad_hatter.decorators.tool import CatTool
from cat.mad_hatter.mad_hatter import MadHatter
from cat.mad_hatter.plugin import Plugin
from cat.log import log
from cat.looking_glass.callbacks import ModelInteractionHandler


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
                if procedures_result.return_direct:
                    # exit agent if a return_direct procedure was executed
                    return procedures_result

                # store intermediate steps to enrich memory chain
                intermediate_steps = procedures_result.intermediate_steps

                # Adding the tools_output key in agent input, needed by the memory chain
                # TODO: find a more elegant way to pass this information
                if len(intermediate_steps) > 0:
                    stray.working_memory.agent_input.tools_output = "## Context of executed system tools: \n"
                    for proc_res in intermediate_steps:
                        # ((step[0].tool, step[0].tool_input), step[1])
                        stray.working_memory.agent_input.tools_output += (
                            f" - {proc_res[0][0]}: {proc_res[1]}\n"
                        )
                return procedures_result

            except Exception as e:
                log.error(e)
                traceback.print_exc()

        return AgentOutput(output="")

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
        allowed_procedures = self.prepare_allowed_procedures(
            stray, recalled_procedures_names
        )

        # Generate the prompt
        prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(
                    template=mad_hatter.execute_hook(
                        "agent_prompt_instructions", prompts.TOOL_PROMPT, cat=stray
                    )
                ),
                *(stray.langchainfy_chat_history()),
            ]
        )

        # Prepare info to fill up the prompt
        prompt_variables = {
            "tools": "\n".join(
                f'- "{tool.name}": {tool.description}'
                for tool in allowed_procedures.values()
            ),
            "tool_names": '"' + '", "'.join(allowed_procedures.keys()) + '"',
            "chat_history": "", #stray.stringify_chat_history(),
            "agent_scratchpad": "",
            "examples": self.generate_examples(allowed_procedures),
        }

        chain = (
            prompt
            | RunnableLambda(lambda x: self._log_prompt(x, "TOOL PROMPT"))
            | stray._llm
            | RunnableLambda(lambda x: self._log_output(x, "TOOL PROMPT OUTPUT"))
            | ChooseProcedureOutputParser()
        )

        llm_action: LLMAction = chain.invoke(
            # convert to dict before passing to langchain
            # TODO: ensure dict keys and prompt placeholders map, so there are no issues on mismatches
            prompt_variables,
            config=RunnableConfig(callbacks=[ModelInteractionHandler(stray, self.__class__.__name__)])
        )

        # execute chosen tool / form
        # loop over allowed tools and forms
        if llm_action.action:
            chosen_procedure = allowed_procedures.get(llm_action.action, None)
            try:
                if Plugin._is_cat_tool(chosen_procedure):
                    # execute tool
                    tool_output = await chosen_procedure._arun(llm_action.action_input, stray=stray)
                    return AgentOutput(
                        output=tool_output,
                        return_direct=chosen_procedure.return_direct,
                        intermediate_steps=[
                            ((llm_action.action, llm_action.action_input), tool_output)
                        ]
                    )
                if Plugin._is_cat_form(chosen_procedure):
                    # create form
                    form_instance = chosen_procedure(stray)
                    # store active form in working memory
                    stray.working_memory.active_form = form_instance
                    # execute form
                    form_output = form_instance.next() # form should be async and should be awaited
                    return AgentOutput(
                        output=form_output["output"],
                        return_direct=True, # we assume forms always do a return_direct
                        intermediate_steps=[
                            ((llm_action.action, ""), form_output["output"])
                        ]
                    )
                
            except Exception as e:
                log.error(f"Error executing {chosen_procedure.procedure_type} `{chosen_procedure.name}`")
                log.error(e)
                traceback.print_exc()

        return AgentOutput(output="")
    
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

        mad_hatter = MadHatter()
        for p in mad_hatter.procedures:
            if p.name in recalled_procedures_names:
                allowed_procedures[p.name] = p

        return allowed_procedures
    
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
                list_examples += """
Question: I have no questions
```json
{{
    "action": "final_answer",
    "action_input": null
}}
```"""
        return list_examples

    
