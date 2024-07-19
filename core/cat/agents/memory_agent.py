
from langchain.prompts import ChatPromptTemplate
from langchain_core.prompts.chat import SystemMessagePromptTemplate
from langchain_core.runnables import RunnableConfig, RunnableLambda
from langchain_core.output_parsers.string import StrOutputParser

from cat.looking_glass.callbacks import NewTokenHandler, ModelInteractionHandler
from cat.agents.base_agent import BaseAgent, AgentOutput

class MemoryAgent(BaseAgent):

    async def execute(self, stray, prompt_prefix, prompt_suffix) -> AgentOutput:
            
        final_prompt = ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(
                    template=prompt_prefix + prompt_suffix
                ),
                *(stray.langchainfy_chat_history()),
            ]
        )

        memory_chain = (
            final_prompt
            | RunnableLambda(lambda x: self._log_prompt(x, "MAIN PROMPT"))
            | stray._llm
            | RunnableLambda(lambda x: self._log_output(x, "MAIN PROMPT OUTPUT"))
            | StrOutputParser()
        )

        output = memory_chain.invoke(
            # convert to dict before passing to langchain
            # TODO: ensure dict keys and prompt placeholders map, so there are no issues on mismatches
            stray.working_memory.agent_input.model_dump(),
            config=RunnableConfig(callbacks=[NewTokenHandler(stray), ModelInteractionHandler(stray, self.__class__.__name__)])
        )

        return AgentOutput(output=output)
    
