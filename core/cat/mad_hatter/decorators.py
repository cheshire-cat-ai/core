from typing import Any, List, Union, Callable
from inspect import signature

from langchain.tools import BaseTool
from langchain.agents import Tool


# Cat hooks manager
class CatHooks:
    __hooks: List = []

    @classmethod
    def reset_hook_list(cls):
        CatHooks.__hooks = []

    @classmethod
    def sort_hooks(cls):
        # CatHooks.__hooks.sort(key=lambda x: x.count, reverse=True)
        CatHooks.__hooks.sort(key=lambda x: x["priority"], reverse=True)
        return CatHooks.__hooks

    # append a hook
    @classmethod
    def add_hook(cls, hook):
        CatHooks.__hooks.append(hook)

    # get hook list
    @classmethod
    def get_hook_list(cls):
        return CatHooks.__hooks


# @hook decorator. Any function in a plugin decorated by @hook and named properly (among list of available hooks) is used by the Cat
# @hook priority defaults to 1, the higher the more important. Hooks in the default core plugin have all priority=0 so they are automatically overwritten from plugins
def hook(_func=None, priority=1) -> Any:
    def decorator(func):
        def cat_hook_wrapper(*args, **kargs):
            return func(*args, **kargs)

        doc_string = func.__doc__
        if doc_string is None:
            doc_string = ""
        CatHooks.add_hook(
            {
                "hook_function": cat_hook_wrapper,
                "hook_name": func.__name__,
                "docstring": func.__doc__,
                "priority": float(priority),
                "count": len(CatHooks.get_hook_list()),
            }
        )

    if _func is None:
        return decorator
    else:
        return decorator(_func)


# All @tool decorated functions in plugins become a CatTool.
# The difference between base langchain Tool and CatTool is that CatTool has an instance of the cat as attribute (set by the MadHatter)
class CatTool(Tool):
    # used by the MadHatter while loading plugins in order to let a Tool access the cat instance
    def set_cat_instance(self, cat_instance):
        self.cat = cat_instance

    def _run(self, input_by_llm):
        return self.func(input_by_llm, cat=self.cat)

    async def _arun(self, input_by_llm):
        # should be used for async Tools, just using sync here
        return self._run(input_by_llm)

    # override `extra = 'forbid'` for Tool pydantic model in langchain
    class Config:
        extra = "allow"


# @tool decorator, a modified version of a langchain Tool that also takes a Cat instance as argument
# adapted from https://github.com/hwchase17/langchain/blob/master/langchain/agents/tools.py
def tool(*args: Union[str, Callable], return_direct: bool = False) -> Callable:
    """Make tools out of functions, can be used with or without arguments.
    Requires:
        - Function must be of type (str) -> str
        - Function must have a docstring
    Examples:
        .. code-block:: python
            @tool
            def search_api(query: str) -> str:
                # Searches the API for the query.
                return
            @tool("search", return_direct=True)
            def search_api(query: str) -> str:
                # Searches the API for the query.
                return
    """

    def _make_with_name(tool_name: str) -> Callable:
        def _make_tool(func: Callable[[str], str]) -> Tool:
            assert func.__doc__, "Function must have a docstring"
            # Description example:
            #   search_api(query: str) - Searches the API for the query.
            description = f"{tool_name}{signature(func)} - {func.__doc__.strip()}"
            tool_ = CatTool(
                name=tool_name,
                func=func,
                description=description,
                return_direct=return_direct,
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
        def _partial(func: Callable[[str], str]) -> BaseTool:
            return _make_with_name(func.__name__)(func)

        return _partial
    else:
        raise ValueError("Too many arguments for tool decorator")
