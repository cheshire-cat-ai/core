import glob
import json
import importlib
from os import path
from inspect import getmembers, isfunction  # , signature

from cat.utils import log, to_camel_case
from cat.mad_hatter.decorators import CatTool, CatHooks


# This class is responsible for plugins functionality:
# - loading
# - prioritizing
# - executing
class MadHatter:
    # loading plugins
    # enter into the plugin folder and loads everthing that is decorated or named properly
    # orders plugged in hooks by name and priority
    # exposes functionality to the cat

    def __init__(self, ccat):
        self.ccat = ccat
        self.hooks, self.tools, self.plugins = self.find_plugins()

    # find all functions in plugin folder decorated with @hook or @tool
    def find_plugins(self):
        # plugins are found in the plugins folder, plus the default core plugin (where default hooks and tools are defined)
        plugin_folders = ["cat/mad_hatter/core_plugin"] + glob.glob("cat/plugins/*")

        all_plugins = []
        all_tools = [] 

        for folder in plugin_folders:
            py_files_path = path.join(folder, "**/*.py")
            log(py_files_path)
            py_files = glob.glob(py_files_path, recursive=True)

            # in order to consider it a plugin makes sure there are py files inside the plugin directory
            if len(py_files) > 0:
                all_plugins.append(self.get_plugin_metadata(folder))

                for py_file in py_files:
                    plugin_name = py_file.replace("/", ".").replace(
                        ".py", ""
                    )  # this is UGLY I know. I'm sorry

                    plugin_module = importlib.import_module(plugin_name)
                    # all_hooks[plugin_name] = dict(
                    #     getmembers(plugin_module, self.is_cat_hook)
                    # )
                    all_tools += getmembers(plugin_module, self.is_cat_tool)

        log("Loaded plugins:")
        log(all_plugins)

        log("Loaded hooks:")
        all_hooks = CatHooks.sort_hooks()
        log(all_hooks)

        log("Loaded tools:")
        all_tools_fixed = []
        for t in all_tools:
            t_fix = t[1]  # it was a tuple, the Tool is the second element
            # fix automatic naming for the Tool (will be used in the prompt)
            # if " - " in t_fix.description:
            #    t_fix.description = t_fix.description.split(" - ")[1] # TODO: show function name and arguments in prompt without repetition and without the cat argument
            # access the cat from any Tool instance (see cat.mad_hatter.decorators)
            t_fix.set_cat_instance(self.ccat)
            all_tools_fixed.append(t_fix)
        log(all_tools_fixed)

        return all_hooks, all_tools_fixed, all_plugins

    # Tries to load the plugin metadata from the provided plugin folder
    def get_plugin_metadata(self, plugin_folder: str):
        plugin_id = path.basename(plugin_folder)
        plugin_json_metadata_file_name = "plugin.json"
        plugin_json_metadata_file_path = path.join(
            plugin_folder, plugin_json_metadata_file_name
        )
        meta = {"id": plugin_id}

        if path.isfile(plugin_json_metadata_file_path):
            try:
                json_file = open(plugin_json_metadata_file_path)
                json_file_data = json.load(json_file)

                meta["name"] = json_file_data["name"]
                meta["description"] = json_file_data["description"]

                json_file.close()

                return meta
            except:
                log(
                    f"Error loading plugin {plugin_folder} metadata, defaulting to generated values"
                )

        meta["name"] = to_camel_case(plugin_id)
        meta[
            "description"
        ] = f"Description not found for this plugin. Please create a `{plugin_json_metadata_file_name}` in the plugin folder."

        return meta

    # a plugin function has to be decorated with @hook (which returns a function named "cat_function_wrapper")
    def is_cat_hook(self, obj):
        return isfunction(obj) and obj.__name__ == "cat_hook_wrapper"

    # a plugin tool function has to be decorated with @tool (which returns an instance of langchain.agents.Tool)
    def is_cat_tool(self, obj):
        return isinstance(obj, CatTool)

    # execute requested hook
    def execute_hook(self, hook_name, hook_input=None):
        for h in self.hooks:
            if hook_name == h["hook_name"]:
                hook = h["hook_function"]
                if hook_input is None:
                    return hook(cat=self.ccat)
                else:
                    return hook(hook_input, cat=self.ccat)

        # every hook must have a default in core_plugin
        raise Exception(f"Hook {hook_name} not present in any plugin")
