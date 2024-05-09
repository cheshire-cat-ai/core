import time
import asyncio
import inspect
import concurrent

from typing import Union, Callable, List 
from inspect import signature

from langchain_core.tools import BaseTool

from cat.log import log

# All @tool decorated functions in plugins become a CatTool.
# The difference between base langchain Tool and CatTool is that CatTool has an instance of the cat as attribute (set by the MadHatter)
class CatTool(BaseTool):

    def __init__(self, name: str, func: Callable, return_direct: bool = False, examples: List[str] = []):

        description = func.__doc__.strip()

        # call parent contructor
        super().__init__(name=name, func=func, description=description, return_direct=return_direct)

        # StrayCat instance will be set by AgentManager
        self.cat = None

        self.func = func
        self.procedure_type = "tool"
        self.name = name
        self.description = description
        self.return_direct = return_direct

        self.triggers_map = {
            "description"  : [
                f"{name}: {description}"
            ],
            "start_example": examples
        }
        # remove cat argument from signature so it does not end up in prompts
        self.signature = f"{signature(self.func)}".replace(", cat)", ")")

    @property
    def start_examples(self):
        return self.triggers_map["start_example"]

    def __repr__(self) -> str:
        return f"CatTool(name={self.name}, return_direct={self.return_direct}, description={self.description})"

    # used by the AgentManager to let a Tool access the cat instance
    def assign_cat(self, cat):
        self.cat = cat

    def _run(self, input_by_llm):
        # Check if the tool is a corutine
        if inspect.iscoroutinefunction(self.func):

            # Wrap the corutine in a function
            def start(coro, *args, **kwargs):
                # Create a new event loop
                loop  = asyncio.new_event_loop()
                # Set the event loop
                asyncio.set_event_loop(loop)
                # Run the tool
                return loop.run_until_complete(coro(input_by_llm, cat=self.cat))
            
            with concurrent.futures.ThreadPoolExecutor() as exe:
                # Run tool in a separete tread
                future = exe.submit(start, self.func, input_by_llm, self.cat)
                # Wait for the result
                return future.result()
                
        # If the tool is a function call it and return the result
        return self.func(input_by_llm, cat=self.cat)

    async def _arun(self, input_by_llm):
        if inspect.iscoroutinefunction(self.func):
            return await self.func(input_by_llm, cat=self.cat)
        
        return await self.cat.loop.run_in_executor(
            None,
            self.func,
            input_by_llm,
            self.cat
        )

    # override `extra = 'forbid'` for Tool pydantic model in langchain
    class Config:
        extra = "allow"
    # TODO should be: (but langchain does not support yet pydantic 2)
    #model_config = ConfigDict(
    #    extra = "allow"
    #)


# @tool decorator, a modified version of a langchain Tool that also takes a Cat instance as argument
# adapted from https://github.com/hwchase17/langchain/blob/master/langchain/agents/tools.py
def tool(*args: Union[str, Callable], return_direct: bool = False, examples: List[str] = []) -> Callable:
    """
    Make tools out of functions, can be used with or without arguments.
    Requires:
        - Function must be of type (str, cat) -> str
        - Function must have a docstring
    Examples:
        .. code-block:: python
            @tool
            def search_api(query: str, cat) -> str:
                # Searches the API for the query.
                return "https://api.com/search?q=" + query
            @tool("search", return_direct=True)
            def search_api(query: str, cat) -> str:
                # Searches the API for the query.
                return "https://api.com/search?q=" + query
    """

    def _make_with_name(tool_name: str) -> Callable:
        def _make_tool(func: Callable[[str], str]) -> CatTool:
            assert func.__doc__, "Function must have a docstring"
            tool_ = CatTool(
                name=tool_name,
                func=func,
                return_direct=return_direct,
                examples=examples,
            )
            return tool_

        return _make_tool

    if len(args) == 1 and isinstance(args[0], str):
        # if the argument is a string, then we use the string as the tool name
        # Example usage: @tool("search", return_direct=True)
        return _make_with_name(args[0])
    elif len(args) == 1 and callable(args[0]):
        # if the argument is a function, then we use the function name as the tool name
        # Example usage: @tool
        return _make_with_name(args[0].__name__)(args[0])
    elif len(args) == 0:
        # if there are no arguments, then we use the function name as the tool name
        # Example usage: @tool(return_direct=True)
        def _partial(func: Callable[[str], str]) -> CatTool:
            return _make_with_name(func.__name__)(func)

        return _partial
    else:
        raise ValueError("Too many arguments for tool decorator")
