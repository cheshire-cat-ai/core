import glob
import importlib
from inspect import getmembers, isfunction  # , signature

import langchain

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
        self.hooks, self.tools = self.find_plugins()

    # find all functions in plugin folder decorated with @hook or @tool
    def find_plugins(self):
        py_files = glob.glob("cat/plugins/**/*.py", recursive=True)

        all_hooks = {}
        all_tools = []
        for py_file in py_files:
            plugin_name = py_file.replace("/", ".").replace(
                ".py", ""
            )  # this is UGLY I know. I'm sorry
            plugin_module = importlib.import_module(plugin_name)
            all_hooks[plugin_name] = dict(getmembers(plugin_module, self.is_cat_hook))
            all_tools += getmembers(plugin_module, self.is_cat_tool)

        log("Loaded hooks:")
        log(all_hooks)

        log("Loaded tools:")
        all_tools_fixed = []
        for t in all_tools:
            t_fix = t[1]  # it was a tuple, the Tool is the second element
            t_fix.description = t_fix.description.split(" - ")[1]
            all_tools_fixed.append(t_fix)
        log(all_tools_fixed)

        # TODO: sort plugins by priority
        return all_hooks, all_tools_fixed

    # a plugin function has to be decorated with @hook (which returns a function named "cat_function_wrapper")
    def is_cat_hook(self, obj):
        return isfunction(obj) and obj.__name__ == "cat_hook_wrapper"

    # a plugin tool function has to be decorated with @tool (which returns an instance of langchain.agents.Tool)
    def is_cat_tool(self, obj):
        return isinstance(obj, langchain.agents.Tool)

    # execute requested hook
    def execute_hook(self, hook_name, hook_input=None):
        # TODO: deal with priority and pipelining
        for plugin_name, plugin in self.hooks.items():
            if hook_name in plugin.keys():
                hook = plugin[hook_name]
                if hook_input is None:
                    return hook()
                else:
                    return hook(hook_input)

        raise Exception(f"Hook {hook_name} not present in any plugin")
