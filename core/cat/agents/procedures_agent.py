import traceback
import random
from typing import Dict

from langchain.prompts import ChatPromptTemplate
from langchain_core.prompts.chat import SystemMessagePromptTemplate
from langchain_core.runnables import RunnableConfig, RunnableLambda

from cat.agents import BaseAgent, AgentOutput
from cat.agents.form_agent import FormAgent
from cat.looking_glass import prompts
from cat.looking_glass.output_parser import ChooseProcedureOutputParser, LLMAction
from cat.experimental.form import CatForm
from cat.mad_hatter.decorators.tool import CatTool
from cat.mad_hatter.mad_hatter import MadHatter
from cat.mad_hatter.plugin import Plugin
from cat.log import log
from cat.looking_glass.callbacks import ModelInteractionHandler
from cat import utils


class ProceduresAgent(BaseAgent):

    form_agent = FormAgent()
    allowed_procedures: Dict[str, CatTool | CatForm] = {}

    def execute(self, stray) -> AgentOutput:
        
        # Run active form if present
        form_output: AgentOutput = self.form_agent.execute(stray)
        if form_output.return_direct:
            return form_output
        
        # Select and run useful procedures
        intermediate_steps = []
        procedural_memories = stray.working_memory.procedural_memories
        if len(procedural_memories) > 0:
            log.debug(f"Procedural memories retrived: {len(procedural_memories)}.")

            try:
                procedures_result: AgentOutput = self.execute_procedures(stray)
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

        return AgentOutput()

    
    def execute_procedures(self, stray):

        # using some hooks
        mad_hatter = MadHatter()

        # get procedures prompt from plugins
        procedures_prompt_template = mad_hatter.execute_hook(
            "agent_prompt_instructions", prompts.TOOL_PROMPT, cat=stray
        )

        # Gather recalled procedures
        recalled_procedures_names: set = self.get_recalled_procedures_names(stray)
        recalled_procedures_names = mad_hatter.execute_hook(
            "agent_allowed_tools", recalled_procedures_names, cat=stray
        )

        # Prepare allowed procedures (tools instances and form classes)
        allowed_procedures: Dict[str, CatTool | CatForm] = \
            self.prepare_allowed_procedures(
                stray, recalled_procedures_names
            )

        # Execute chain and obtain a choice of procedure from the LLM
        llm_action: LLMAction = self.execute_chain(stray, procedures_prompt_template, allowed_procedures)

        # route execution to subagents
        return self.execute_subagents(stray, llm_action, allowed_procedures)


    def execute_chain(self, stray, procedures_prompt_template, allowed_procedures) -> LLMAction:
        
        # Prepare info to fill up the prompt
        prompt_variables = {
            "tools": "\n".join(
                f'- "{tool.name}": {tool.description}'
                for tool in allowed_procedures.values()
            ),
            "tool_names": '"' + '", "'.join(allowed_procedures.keys()) + '"',
            #"chat_history": stray.stringify_chat_history(),
            "examples": self.generate_examples(allowed_procedures),
        }

        # Ensure prompt inputs and prompt placeholders map
        prompt_variables, procedures_prompt_template = \
            utils.match_prompt_variables(prompt_variables, procedures_prompt_template)

        # Generate prompt
        prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(
                    template=procedures_prompt_template
                ),
                *(stray.langchainfy_chat_history()),
            ]
        )

        chain = (
            prompt
            | RunnableLambda(lambda x: utils.langchain_log_prompt(x, "TOOL PROMPT"))
            | stray._llm
            | RunnableLambda(lambda x: utils.langchain_log_output(x, "TOOL PROMPT OUTPUT"))
            | ChooseProcedureOutputParser() # ensures output is a LLMAction
        )

        llm_action: LLMAction = chain.invoke(
            prompt_variables,
            config=RunnableConfig(callbacks=[ModelInteractionHandler(stray, self.__class__.__name__)])
        )

        return llm_action
    
    
    def execute_subagents(self, stray, llm_action, allowed_procedures):
        # execute chosen tool / form
        # loop over allowed tools and forms
        if llm_action.action:
            chosen_procedure = allowed_procedures.get(llm_action.action, None)
            try:
                if Plugin._is_cat_tool(chosen_procedure):
                    # execute tool
                    tool_output = chosen_procedure.run(llm_action.action_input, stray=stray)
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
                    return self.form_agent.execute(stray)
                
            except Exception as e:
                log.error(f"Error executing {chosen_procedure.procedure_type} `{chosen_procedure.name}`")
                log.error(e)
                traceback.print_exc()

        return AgentOutput(output="")

    
    def get_recalled_procedures_names(self, stray) -> set:
        recalled_procedures_names = set()
        for p in stray.working_memory.procedural_memories:
            p_type = p[0].metadata["type"]
            p_trigger_type = p[0].metadata["trigger_type"]
            p_source = p[0].metadata["source"]
            if p_type in ["tool", "form"] \
                and p_trigger_type in ["description", "start_example"]:
                recalled_procedures_names.add(p_source)
        return recalled_procedures_names
    
    def prepare_allowed_procedures(
            self,
            stray,
            recalled_procedures_names
        ) -> Dict[str, CatTool | CatForm]:
        
        allowed_procedures: Dict[str, CatTool | CatForm] = {}

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
    "action_input": "...input here..."
}}"""
                list_examples += f"\nQuestion: {random.choice(proc.start_examples)}"
                list_examples += f"\n```json\n{example_json}\n```"
                list_examples += """
Question: I have no questions
```json
{
    "action": "no_answer",
    "action_input": null
}
```"""
        return list_examples

    
