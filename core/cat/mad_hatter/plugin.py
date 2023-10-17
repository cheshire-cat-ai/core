import os
import sys
import json
import glob
import importlib
import traceback
from typing import Dict
from inspect import getmembers
from pydantic import BaseModel

from cat.mad_hatter.decorators import CatTool, CatHook, CatPluginOverride
from cat.utils import to_camel_case
from cat.log import log, get_log_level


# Empty class to represent basic plugin Settings model
class PluginSettingsModel(BaseModel):
    pass


# this class represents a plugin in memory
# the plugin itsefl is managed as much as possible unix style
#      (i.e. by saving information in the folder itself)

class Plugin:

    def __init__(self, plugin_path: str):
        
        # does folder exist?
        if not os.path.exists(plugin_path) or not os.path.isdir(plugin_path):
            raise Exception(f"{plugin_path} does not exist or is not a folder. Cannot create Plugin.")

        # where the plugin is on disk
        self._path: str = plugin_path

        # search for .py files in folder
        py_files_path = os.path.join(self._path, "**/*.py")
        self.py_files = glob.glob(py_files_path, recursive=True)

        if len(self.py_files) == 0:
            raise Exception(f"{plugin_path} does not contain any python files. Cannot create Plugin.")

        # plugin id is just the folder name
        self._id: str = os.path.basename(os.path.normpath(plugin_path))

        # plugin manifest (name, decription, thumb, etc.)
        self._manifest = self._load_manifest()

        self._install_requirements()

        # list of tools and hooks contained in the plugin.
        #   The MadHatter will cache them for easier access,
        #   but they are created and stored in each plugin instance
        self._hooks = [] 
        self._tools = []

        # list of @plugin decorated functions overrriding default plugin behaviour
        self._plugin_overrides = [] # TODO: make this a dictionary indexed by func name, for faster access

        # plugin starts deactivated
        self._active = False

    def activate(self):
        # lists of hooks and tools
        self._hooks, self._tools, self._plugin_overrides = self._load_decorated_functions()
        self._active = True

    def deactivate(self):
        # Remove the imported modules
        for py_file in self.py_files:
            py_filename = py_file.replace("/", ".").replace(".py", "")

            # If the module is imported it is removed
            if py_filename in sys.modules:
                log.debug(f"Remove module {py_filename}")
                sys.modules.pop(py_filename)
        
        self._hooks = []
        self._tools = []
        self._plugin_overrides = []
        self._active = False

    # get plugin settings JSON schema
    def settings_schema(self):

        # is "plugin_settings_schema" hook defined in the plugin?
        for h in self._plugin_overrides:
            if h.name == "settings_schema":
                return h.function()

        # default schema (empty)
        return PluginSettingsModel.model_json_schema()

    # load plugin settings
    def load_settings(self):

        # is "plugin_settings_load" hook defined in the plugin?
        for h in self._plugin_overrides:
            if h.name == "load_settings":
                return h.function()

        # by default, plugin settings are saved inside the plugin folder
        #   in a JSON file called settings.json
        settings_file_path = os.path.join(self._path, "settings.json")

        # default settings is an empty dictionary
        settings = {}

        # load settings.json if exists
        if os.path.isfile(settings_file_path):
            try:
                with open(settings_file_path, "r") as json_file:
                    settings = json.load(json_file)
            except Exception as e:
                log.error(f"Unable to load plugin {self._id} settings")
                log.error(e)

        return settings
    
    # save plugin settings
    def save_settings(self, settings: Dict):

        # is "plugin_settings_save" hook defined in the plugin?
        for h in self._plugin_overrides:
            if h.name == "save_settings":
                return h.function(settings)

        # by default, plugin settings are saved inside the plugin folder
        #   in a JSON file called settings.json
        settings_file_path = os.path.join(self._path, "settings.json")
        
        # load already saved settings
        old_settings = self.load_settings()
        
        # overwrite settings over old ones
        updated_settings = { **old_settings, **settings }

        # write settings.json in plugin folder
        try:
            with open(settings_file_path, "w") as json_file:
                json.dump(updated_settings, json_file, indent=4)
        except Exception:
            log.error(f"Unable to save plugin {self._id} settings")
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
                log.info(f"Loading plugin {self._path} metadata, defaulting to generated values")

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
    
    def _install_requirements(self):
        req_file = os.path.join(self.path, "requirements.txt")

        if os.path.exists(req_file):
            log.info(f"Installing requirements for: {self.id}")
            os.system(f'pip install --no-cache-dir -r "{req_file}"')


    # lists of hooks and tools
    def _load_decorated_functions(self):
        hooks = []
        tools = []
        plugin_overrides = []

        for py_file in self.py_files:
            py_filename = py_file.replace("/", ".").replace(".py", "")  # this is UGLY I know. I'm sorry

            log.info(f"Import module {py_filename}")

            # save a reference to decorated functions
            try:
                plugin_module = importlib.import_module(py_filename)
                hooks += getmembers(plugin_module, self._is_cat_hook)
                tools += getmembers(plugin_module, self._is_cat_tool)
                plugin_overrides += getmembers(plugin_module, self._is_cat_plugin_override)
            except Exception as e:
                log.error(f"Error in {py_filename}: {str(e)}")
                traceback.print_exc()
                raise Exception(f"Unable to load the plugin {self._id}")
            
        # clean and enrich instances
        hooks = list(map(self._clean_hook, hooks))
        tools = list(map(self._clean_tool, tools))
        plugin_overrides = list(map(self._clean_plugin_override, plugin_overrides))

        return hooks, tools, plugin_overrides

    def _clean_hook(self, hook):
        # getmembers returns a tuple
        h = hook[1]
        h.plugin_id = self._id
        return h

    def _clean_tool(self, tool):
        # getmembers returns a tuple
        t = tool[1]
        t.plugin_id = self._id
        return t
    
    def _clean_plugin_override(self, plugin_override):
        # getmembers returns a tuple
        return plugin_override[1]

    # a plugin hook function has to be decorated with @hook
    # (which returns an instance of CatHook)
    @staticmethod
    def _is_cat_hook(obj):
        return isinstance(obj, CatHook)

    # a plugin tool function has to be decorated with @tool
    # (which returns an instance of CatTool)
    @staticmethod
    def _is_cat_tool(obj):
        return isinstance(obj, CatTool)
    
    # a plugin override function has to be decorated with @plugin
    # (which returns an instance of CatPluginOverride)
    @staticmethod
    def _is_cat_plugin_override(obj):
        return isinstance(obj, CatPluginOverride)
    
    @property
    def path(self):
        return self._path
    
    @property
    def id(self):
        return self._id
    
    @property
    def manifest(self):
        return self._manifest
    
    @property
    def active(self):
        return self._active

    @property
    def hooks(self):
        return self._hooks
    
    @property
    def tools(self):
        return self._tools
