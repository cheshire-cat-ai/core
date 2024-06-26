
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_core.prompts.chat import SystemMessagePromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers.string import StrOutputParser
from langchain_core.utils import get_colored_text

from cat.log import log
from cat.looking_glass.callbacks import NewTokenHandler

class MemoryAgent:

    async def execute(self, stray, prompt_prefix, prompt_suffix):
            
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
            | RunnableLambda(lambda x: self.__log_prompt(x))
            | stray._llm
            | StrOutputParser()
        )

        stray.working_memory.agent_input.output = memory_chain.invoke(
            # convert to dict before passing to langchain
            # TODO: ensure dict keys and prompt placeholders map, so there are no issues on mismatches
            stray.working_memory.agent_input.dict(),
            config=RunnableConfig(callbacks=[NewTokenHandler(stray)])
        )

        return stray.working_memory.agent_input
    
    def __log_prompt(self, x):
        # The names are not shown in the chat history log, the model however receives the name correctly
        log.info(
            "The names are not shown in the chat history log, the model however receives the name correctly"
        )
        print("\n", get_colored_text(x.to_string(), "green"))
        return x