import os
import json
import glob
import importlib
from typing import Dict
from inspect import getmembers, isfunction  # , signature
from pydantic import BaseModel

from cat.mad_hatter.decorators import CatTool, CatHook
from cat.utils import to_camel_case
from cat.log import log

# this class represents a plugin in memory
# the plugin itsefl is managed as much as possible unix style
#      (i.e. by saving information in the folder itself)

class Plugin:

    def __init__(self, plugin_path: str, active: bool):

        # where the plugin is on disk
        self.path: str = plugin_path

        # plugin id is just the folder name
        self.id: str = os.path.basename(os.path.normpath(plugin_path))

        # plugin manifest (name, decription, thumb, etc.)
        self.manifest = self.load_manifest()

        # list of tools and hooks contained in the plugin.
        #   The MadHatter will cache them for easier access,
        #   but they are created and stored in each plugin instance
        self.hooks = []
        self.tools = []

        # all plugins start active, they can be deactivated/reactivated from endpoint
        if active:
            self.activate()
        else:
            self.deactivate()
    

    def activate(self):
        # lists of hooks and tools
        self.load_hooks_and_tools()

    def deactivate(self):
        self.hooks = []
        self.tools = []

    # get plugin settings JSON schema
    def get_settings_schema(self):

        # is "plugin_settings_schema" hook defined in the plugin?
        for h in self.hooks:
            if h.name == "plugin_settings_schema":
                return h.function()

        # default schema (empty)
        return BaseModel.schema()

    # load plugin settings
    def load_settings(self):

        # is "plugin_settings_load" hook defined in the plugin?
        for h in self.hooks:
            if h.name == "plugin_settings_load":
                return h.function()

        # by default, plugin settings are saved inside the plugin folder
        #   in a JSON file called settings.json
        settings_file_path = os.path.join(self.path, "settings.json")

        # default settings is an empty dictionary
        settings = {}

        # load settings.json if exists
        if os.path.isfile(settings_file_path):
            try:
                with open(settings_file_path, "r") as json_file:
                    settings = json.load(json_file)
            except Exception as e:
                log(f"Unable to load plugin {self.id} settings", "ERROR")
                log(e, "ERROR")

        return settings
    
    # save plugin settings
    def save_settings(self, settings: Dict):

        # is "plugin_settings_save" hook defined in the plugin?
        for h in self.hooks:
            if h.name == "plugin_settings_save":
                return h.function(settings)

        # by default, plugin settings are saved inside the plugin folder
        #   in a JSON file called settings.json
        settings_file_path = os.path.join(self.path, "settings.json")
        
        # load already saved settings
        old_settings = self.load_settings()
        
        # overwrite settings over old ones
        updated_settings = { **old_settings, **settings }

        # write settings.json in plugin folder
        try:
            with open(settings_file_path, "w") as json_file:
                json.dump(updated_settings, json_file, indent=4)
        except Exception:
            log(f"Unable to save plugin {self.id} settings", "ERROR")
            return {}
    
        return updated_settings

    def _load_manifest(self):

        plugin_json_metadata_file_name = "plugin.json"
        plugin_json_metadata_file_path = os.path.join(self._path, plugin_json_metadata_file_name)
        meta = {"id": self._id}
        json_file_data = {}

        if os.path.isfile(plugin_json_metadata_file_path):
            try:
                json_file = open(plugin_json_metadata_file_path)
                json_file_data = json.load(json_file)
                json_file.close()
            except Exception:
                log(f"Loading plugin {self._path} metadata, defaulting to generated values", "INFO")

        meta["name"] = json_file_data.get("name", to_camel_case(self._id))
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

    # lists of hooks and tools
    def load_hooks_and_tools(self):

        # search for .py files in folder
        py_files_path = os.path.join(self.path, "**/*.py")
        py_files = glob.glob(py_files_path, recursive=True)

        self.hooks = []
        self.tools = []

        for py_file in py_files:
            py_filename = py_file.replace("/", ".").replace(".py", "")  # this is UGLY I know. I'm sorry

            # save a reference to decorated functions
            plugin_module = importlib.import_module(py_filename)
            self.hooks += getmembers(plugin_module, self.is_cat_hook)
            self.tools += getmembers(plugin_module, self.is_cat_tool)

        # clean and enrich instances
        self.hooks = list(map(self.clean_hook, self.hooks))
        self.tools = list(map(self.clean_tool, self.tools))

    def clean_hook(self, hook):
        # getmembers returns a tuple
        h = hook[1]
        h.plugin_id = self.id
        return h

    def clean_tool(self, tool):
        # getmembers returns a tuple
        t = tool[1]
        t.plugin_id = self.id
        return t

    # a plugin hook function has to be decorated with @hook
    # (which returns an instance of CatHook)
    def is_cat_hook(self, obj):
        return isinstance(obj, CatHook)

    # a plugin tool function has to be decorated with @tool
    # (which returns an instance of CatTool)
    def is_cat_tool(self, obj):
        return isinstance(obj, CatTool)
    