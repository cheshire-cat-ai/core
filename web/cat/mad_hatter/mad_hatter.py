import glob
import importlib
from inspect import getmembers, isfunction  # , signature

from cat.utils import log


# This class is responsible for plugins functionality:
# - loading
# - prioritizing
# - executing
class MadHatter:
    # loading plugins
    # enter into the plugin folder and loads everthing that is decorated or named properly
    # orders plugged in hooks by name and priority
    # exposes functionality to the cat

    def __init__(self):
        self.plugins = self.find_plugins()

    # find all functions in plugin folder decorated with @hook or @tool
    def find_plugins(self):
        py_files = glob.glob("cat/plugins/**/*.py", recursive=True)

        all_hooks = {}
        for py_file in py_files:
            plugin_name = py_file.replace("/", ".").replace(
                ".py", ""
            )  # this is UGLY I know. I'm sorry
            plugin_module = importlib.import_module(plugin_name)
            all_hooks[plugin_name] = dict(getmembers(plugin_module, self.is_cat_hook))

        log("Loaded plugins:")
        log(all_hooks)

        # TODO: sort plugins by priority
        return all_hooks

    # a plugin function has to be decorated with @hook (which returns a function named "cat_function_wrapper")
    def is_cat_hook(self, func):
        return isfunction(func) and (
            (func.__name__ == "cat_hook_wrapper")
            or ((func.__name__ == "cat_tool_wrapper"))
        )

    # execute requested hook
    def execute_hook(self, hook_name, hook_input=None):
        # TODO: deal with priority and pipelining
        for plugin_name, plugin in self.plugins.items():
            if hook_name in plugin.keys():
                hook = plugin[hook_name]
                if hook_input is None:
                    return hook()
                else:
                    return hook(hook_input)

        raise Exception(f"Hook {hook_name} not present in any plugin")
