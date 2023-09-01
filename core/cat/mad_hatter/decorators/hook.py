from typing import Union, Callable
# class to represent a @hook
class CatHook:

    def __init__(self, function: Callable, priority: int, hook_name: str = ""):
        
        self.function = function
        self.name = hook_name if hook_name else function.__name__
        self.priority = float(priority)

    def __repr__(self) -> str:
        return f"CatHook:\n - name: {self.name}, \n - priority: {self.priority}"

# @hook decorator. Any function in a plugin decorated by @hook and named properly (among list of available hooks) is used by the Cat
# @hook priority defaults to 1, the higher the more important. Hooks in the default core plugin have all priority=0 so they are automatically overwritten from plugins
def hook(*args: Union[str, Callable], priority: int = 1, hook_name: str = "") -> Callable:
    def make_hook(func):
        return CatHook(
            func,
            priority=priority,
            hook_name=hook_name
        )
    
    if len(args) == 1 and callable(args[0]):
        # called as @hook
        return CatHook(
            function=args[0],
            priority=priority,
            hook_name=hook_name
        )
    else:
        # called as @hook(*args, **kwargs)
        return make_hook
