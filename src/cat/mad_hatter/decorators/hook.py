from typing import Union, Callable


# class to represent a @hook
class CatHook:
    def __init__(self, name: str, func: Callable, priority: int):
        self.function = func
        self.name = name
        self.priority = priority

    def __repr__(self) -> str:
        return f"CatHook(name={self.name}, priority={self.priority})"


# @hook decorator. Any function in a plugin decorated by @hook and named properly (among list of available hooks) is used by the Cat
# @hook priority defaults to 1, the higher the more important. Hooks in the default core plugin have all priority=0 so they are automatically overwritten from plugins
def hook(*args: Union[str, Callable], priority: int = 1) -> Callable:
    """
    Make hooks out of functions, can be used with or without arguments.
    Examples:
        .. code-block:: python
            @hook
            def on_message(message: Message) -> str:
                return "Hello!"
            @hook("on_message", priority=2)
            def on_message(message: Message) -> str:
                return "Hello!"
    """

    def _make_with_name(hook_name: str) -> Callable:
        def _make_hook(func: Callable[[str], str]) -> CatHook:
            hook_ = CatHook(name=hook_name, func=func, priority=priority)
            return hook_

        return _make_hook

    if len(args) == 1 and isinstance(args[0], str):
        # if the argument is a string, then we use the string as the hook name
        # Example usage: @hook("search", priority=2)
        return _make_with_name(args[0])
    elif len(args) == 1 and callable(args[0]):
        # if the argument is a function, then we use the function name as the hook name
        # Example usage: @hook
        return _make_with_name(args[0].__name__)(args[0])
    elif len(args) == 0:
        # if there are no arguments, then we use the function name as the hook name
        # Example usage: @hook(priority=2)
        def _partial(func: Callable[[str], str]) -> CatHook:
            return _make_with_name(func.__name__)(func)

        return _partial
    else:
        raise ValueError("Too many arguments for hook decorator")
