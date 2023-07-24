
# class to represent a @hook
class CatHook:

    def __init__(self, function, priority=1):
        
        self.function = function
        self.name = function.__name__
        self.priority = float(priority)

    def __repr__(self) -> str:
        return f"CatHook:\n - name: {self.name}, \n - priority: {self.priority}"

# @hook decorator. Any function in a plugin decorated by @hook and named properly (among list of available hooks) is used by the Cat
# @hook priority defaults to 1, the higher the more important. Hooks in the default core plugin have all priority=0 so they are automatically overwritten from plugins
def hook(*args, **kwargs):
    def make_hook(func):
        return CatHook(
            func,
            kwargs.get("priority", 1),
        )
    
    if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
        # called as @hook
        return CatHook(args[0])
    else:
        # called as @hook(*args, **kwargs)
        return make_hook
