import os
import json
import glob
import importlib
from typing import Dict
from inspect import getmembers, isfunction  # , signature

from cat.mad_hatter.decorators import CatTool, CatHook
from cat.utils import to_camel_case
from cat.log import log

# this class represents a plugin in memory
# the plugin itsefl is managed as much as possible unix style
#      (i.e. by saving information in the folder itself)

class Plugin:

    def __init__(self, plugin_absolute_path):

        # where the plugin is on disk
        self.path: str = plugin_absolute_path

        # plugin id is just the folder name
        self.id: str = os.path.basename(os.path.normpath(plugin_absolute_path))

        # all plugins start inactive
        self.active: bool = False

        # plugin manifest (name, decription, thumb, etc.)
        self.manifest = self.load_manifest()

        # plugin settings
        self.settings = self.load_settings()

        # lists of hooks and tools
        self.hooks, self.tools = self.load_hooks_and_tools()


    # load contents of plugin.json (if exists)
    def load_manifest(self):

        plugin_json_metadata_file_name = "plugin.json"
        plugin_json_metadata_file_path = os.path.join(self.path, plugin_json_metadata_file_name)
        meta = {"id": self.id}
        json_file_data = {}

        if os.path.isfile(plugin_json_metadata_file_path):
            try:
                json_file = open(plugin_json_metadata_file_path)
                json_file_data = json.load(json_file)
                json_file.close()
            except Exception:
                log(f"Loading plugin {self.path} metadata, defaulting to generated values", "INFO")

        meta["name"] = json_file_data.get("name", to_camel_case(self.id))
        meta["description"] = json_file_data.get("description", (
            "Description not found for this plugin. "
            f"Please create a `{plugin_json_metadata_file_name}`"
            " in the plugin folder."
        ))
        meta["author_name"] = json_file_data.get("author_name", "Unknown author")
        meta["author_url"] = json_file_data.get("author_url", "")
        meta["plugin_url"] = json_file_data.get("plugin_url", "")
        meta["tags"] = json_file_data.get("tags", "unknown")
        meta["thumb"] = json_file_data.get("thumb", "")
        meta["version"] = json_file_data.get("version", "0.0.1")

        return meta

    # load plugin settings
    def get_settings_schema(self):
        return None

    # load plugin settings
    def load_settings(self):
        #settings_file_path = os.path.join("cat/plugins", plugin_id, "settings.json")
        #settings = { "active": False }

        #if os.path.isfile(settings_file_path):
        #    try:
        #        json_file = open(settings_file_path)
        #        settings = json.load(json_file)
        #        if "active" not in settings:
        #            settings["active"] = False
        #        json_file.close()
        #    except Exception:
        #        log(f"Loading plugin {plugin_id} settings, defaulting to -> 'active': False", "INFO")
    
        #return settings
        return {}
    
    # save plugin settings
    def save_settings(self, settings: Dict):

        #settings_file_path = os.path.join("cat/plugins", plugin_id, "settings.json")
        #updated_settings = settings

        #try:
        #    json_file = open(settings_file_path, 'r+')
        #    current_settings = json.load(json_file)
        #    json_file.close()
        #    updated_settings = { **current_settings, **settings }
        #    json_file = open(settings_file_path, 'w')
        #    json.dump(updated_settings, json_file, indent=4)
        #    json_file.close()
        #except Exception:
        #    log(f"Unable to save plugin {plugin_id} settings", "INFO")
    
        #return updated_settings
        return {}


    # lists of hooks and tools
    def load_hooks_and_tools(self):

        # search for .py files in folder
        py_files_path = os.path.join(self.path, "**/*.py")
        log(py_files_path, "WARNING")
        py_files = glob.glob(py_files_path, recursive=True)

        hooks = []
        tools = []

        for py_file in py_files:
            py_filename = py_file.replace("/", ".").replace(".py", "")  # this is UGLY I know. I'm sorry

            # save a reference to decorated functions
            plugin_module = importlib.import_module(py_filename)
            hooks += getmembers(plugin_module, self.is_cat_hook)
            tools += getmembers(plugin_module, self.is_cat_tool)

        # clean unnecessary tuples
        hooks = list(map(lambda h: h[1], hooks))
        tools = list(map(lambda t: t[1], tools))

        for h in hooks:
            log(h, "ERROR")
            log('-'*50, "ERROR")

        for t in tools:
            log(t, "ERROR")
            log('-'*50, "ERROR")

        return hooks, tools

    '''
        log("Hooks loading", "INFO")
        all_hooks = CatHooks.sort_hooks()
        for hook in all_hooks:
            log("> " + hook["hook_name"])

        log("Tools loading")
        all_tools_fixed = []
        for t in all_tools:
            t_fix = t[1]  # it was a tuple, the Tool is the second element

            # Prepare the tool to be used in the Cat (setting the cat instanca, adding properties)
            t_fix.augment_tool(self.ccat)

            all_tools_fixed.append(t_fix)
        log(all_tools_fixed, "INFO")

        self.hooks, self.tools, self.plugins = all_hooks, all_tools_fixed, all_plugins
    '''

    # a plugin hook function has to be decorated with @hook
    # (which returns an instance of CatHook)
    def is_cat_hook(self, obj):
        return isinstance(obj, CatHook)


    # a plugin tool function has to be decorated with @tool
    # (which returns an instance of CatTool)
    def is_cat_tool(self, obj):
        return isinstance(obj, CatTool)
    











    