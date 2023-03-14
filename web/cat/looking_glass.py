
import os
import time

from cat import config
from cat.rabbit_hole import ingest_file
from cat.agent_manager import AgentManager
from cat.memory import get_vector_store
from cat.utils import log


# main class representing the cat
class CheshireCat:


    def __init__(self, verbose=False):

        self.verbose = verbose
        
        # bootstrap the cat!
        self.load_core()
        self.load_plugins()
        self.load_agent()

        # recent conversation # TODO: load from episodic memory latest conversation messages
        self.history = ''


    def load_core(self):
        
        # TODO: llm and embedder should be loaded from db after the user has set them up
        # TODO: remove .env configuration
        self.llm      = config.LANGUAGE_MODEL
        self.embedder = config.LANGUAGE_EMBEDDER

        #        # HyDE chain TODO
#        hypothesis_prompt = PromptTemplate(
#            input_variables=['question'],
#            template='''What could be a plausible answer to the following question? Be concise and invent the answer even if you don't know it.
#
#Question:
#{question}
#
#Answer:
#'''
#        )

#        hypothetis_chain = LLMChain(
#            prompt=hypothesis_prompt,
#            llm=self.llm,
#            verbose=True
#        )


        ### Memory
        self.episodic_memory    = get_vector_store('episodes', embedder=self.embedder)
        self.declarative_memory = get_vector_store('documents', embedder=self.embedder)
        # TODO: don't know if it is better to use different collections or just different metadata

        ### Agent
        # let's cutomize ...every aspect of agent prompt
        self.prefix_prompt = config.MAIN_PROMPT_PREFIX
        
        self.suffix_prompt = config.MAIN_PROMPT_SUFFIX
        
        # TODO: can input vars just be deducted from the prompt? What about plugins?
        self.input_variables = [
            'input',
            'chat_history',
            'episodic_memory',
            'declarative_memory',
            'agent_scratchpad'
        ]

        
    def load_plugins(self):
        # TODO: load pluging / extensions
        pass


    def load_agent(self):

        self.agent_manager = AgentManager(llm=self.llm, tool_names=['llm-math', 'python_repl']) # TODO: load from plugins
        #am.set_tools(['llm-math', 'python_repl']) 
        self.agent_executor = self.agent_manager.get_agent_executor(
            prefix_prompt=self.prefix_prompt,
            suffix_prompt=self.suffix_prompt,
            input_variables=self.input_variables,
            return_intermediate_steps=True,
        )


    # retrieve conversation memories (things user said in conversation)
    def recall_episodic_memories(self, user_message):

        memories_separator = '\n  - '
            
        # retrieve conversation memories
        # TODO: HyDE
        # TODO: choose return format (list vs string)
        episodic_memory_vectors = self.episodic_memory.max_marginal_relevance_search(user_message) # TODO: customize k and fetch_k
        episodic_memory_text = [m.page_content.replace('\n', '. ') for m in episodic_memory_vectors]
        episodic_memory_content = memories_separator + memories_separator.join(episodic_memory_text) # TODO: take away duplicates; insert time information (e.g "two days ago")

        return episodic_memory_content

    # retrieve external memories (uploaded documents)
    def recall_declarative_memories(self, user_message):

        memories_separator = '\n  - '
    
        # retrieve from uploaded documents
        # TODO: HyDE
        # TODO: choose return format (list vs string)
        declarative_memory_vectors = self.declarative_memory.max_marginal_relevance_search(user_message) # TODO: customize k and fetch_k
        log(declarative_memory_vectors)
        declarative_memory_text = [m.page_content.replace('\n', '. ') for m in declarative_memory_vectors]
        declarative_memory_content = memories_separator + memories_separator.join(declarative_memory_text) # TODO: take away duplicates; insert SOURCE information

        return declarative_memory_content


    def __call__(self, user_message):
            
            if self.verbose:
                log(user_message)

            # recall relevant memories
            episodic_memory_content    = self.recall_episodic_memories(user_message) # TODO: choose return format (list vs string)
            declarative_memory_content = self.recall_declarative_memories(user_message)
                   
            # reply with agent
            cat_message = self.agent_executor({
                'input': user_message,
                'episodic_memory': episodic_memory_content,
                'declarative_memory': declarative_memory_content,
                'chat_history': self.history,
            })

            if self.verbose:
                log(cat_message)
            
            # update conversation history
            self.history += f'Human: {user_message}\n'
            self.history += f'AI: {cat_message["output"]}\n'        
            
            # store user message in episodic memory
            # TODO: also embed HyDE style
            # TODO: vectorize and store conversation chunks (not raw dialog, but summarization)
            vector_ids = self.episodic_memory.add_texts(
                [user_message],
                [{
                    'source' : 'user',
                    'when': time.time(),
                    'text': user_message,
                }]
            )

            # build data structure for output (response and why with memories)
            final_output = {
                'error': False,
                'content': cat_message['output'],
                'why'    : {
                    **cat_message,
                    'episodic_memory'    : episodic_memory_content,
                    'declarative_memory' : declarative_memory_content, #TODO: add sources
                },
            }

            return final_output