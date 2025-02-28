import os
import sys
import json
import glob
import tempfile
import importlib
import subprocess
from typing import Dict, List
from inspect import getmembers, isclass
from pydantic import BaseModel, ValidationError
from packaging.requirements import Requirement

from cat.mad_hatter.decorators import CatTool, CatHook, CatPluginDecorator, CustomEndpoint
from cat.experimental.form import CatForm
from cat.utils import to_camel_case
from cat.log import log


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
            raise Exception(
                f"{plugin_path} does not exist or is not a folder. Cannot create Plugin."
            )

        # where the plugin is on disk
        self._path: str = plugin_path

        # search for .py files in folder
        py_files_path = os.path.join(self._path, "**/*.py")
        self.py_files = glob.glob(py_files_path, recursive=True)

        if len(self.py_files) == 0:
            raise Exception(
                f"{plugin_path} does not contain any python files. Cannot create Plugin."
            )

        # plugin id is just the folder name
        self._id: str = os.path.basename(os.path.normpath(plugin_path))

        # plugin manifest (name, decription, thumb, etc.)
        self._manifest = self._load_manifest()

        # list of tools, forms and hooks contained in the plugin.
        #   The MadHatter will cache them for easier access,
        #   but they are created and stored in each plugin instance
        self._hooks: List[CatHook] = []  # list of plugin hooks
        self._tools: List[CatTool] = []  # list of plugin tools
        self._forms: List[CatForm] = []  # list of plugin forms
        self._endpoints: List[CustomEndpoint] = [] # list of plugin endpoints

       # list of @plugin decorated functions overriding default plugin behaviour
        self._plugin_overrides = {}

        # plugin starts deactivated
        self._active = False

    def activate(self):
        # install plugin requirements on activation
        try:
            self._install_requirements()
        except Exception as e:
            raise e

        # Load of hook, tools, forms and endpoints
        self._load_decorated_functions()

        # by default, plugin settings are saved inside the plugin folder
        #   in a JSON file called settings.json
        settings_file_path = os.path.join(self._path, "settings.json")

        # Try to create setting.json
        if not os.path.isfile(settings_file_path):
            self._create_settings_from_model()

        self._active = True

        # run custom activation from @plugin
        if "activated" in self.overrides:
            self.overrides["activated"].function(self)

    def deactivate(self):

        # run custom deactivation from @plugin
        if "deactivated" in self.overrides:
            self.overrides["deactivated"].function(self)

        # Remove the imported modules
        for py_file in self.py_files:
            py_filename = py_file.replace("/", ".").replace(".py", "")

            # If the module is imported it is removed
            if py_filename in sys.modules:
                log.debug(f"Remove module {py_filename}")
                sys.modules.pop(py_filename)

        self._hooks = []
        self._tools = []
        self._forms = []
        self._deactivate_endpoints()
        self._plugin_overrides = {}
        self._active = False

    # get plugin settings JSON schema
    def settings_schema(self):
        # is "settings_schema" hook defined in the plugin?
        if "settings_schema" in self.overrides:
            return self.overrides["settings_schema"].function()
        else:
            # if the "settings_schema" is not defined but
            # "settings_model" is it gets the schema from the model
            if "settings_model" in self.overrides:
                return self.overrides["settings_model"].function().model_json_schema()

        # default schema (empty)
        return PluginSettingsModel.model_json_schema()

    # get plugin settings Pydantic model
    def settings_model(self):
        # is "settings_model" hook defined in the plugin?
        if "settings_model" in self.overrides:
            return self.overrides["settings_model"].function()

        # default schema (empty)
        return PluginSettingsModel

    # load plugin settings
    def load_settings(self):
        # is "settings_load" hook defined in the plugin?
        if "load_settings" in self.overrides:
            return self.overrides["load_settings"].function()

        # by default, plugin settings are saved inside the plugin folder
        #   in a JSON file called settings.json
        settings_file_path = os.path.join(self._path, "settings.json")

        if not os.path.isfile(settings_file_path):
            if not self._create_settings_from_model():
                return {}

        # load settings.json if exists
        if os.path.isfile(settings_file_path):
            try:
                with open(settings_file_path, "r") as json_file:
                    settings = json.load(json_file)
                    return settings

            except Exception as e:
                log.error(f"Unable to load plugin {self._id} settings.")
                log.warning(self.plugin_specific_error_message())
                raise e

    # save plugin settings
    def save_settings(self, settings: Dict):
        # is "settings_save" hook defined in the plugin?
        if "save_settings" in self.overrides:
            return self.overrides["save_settings"].function(settings)

        # by default, plugin settings are saved inside the plugin folder
        #   in a JSON file called settings.json
        settings_file_path = os.path.join(self._path, "settings.json")

        # load already saved settings
        old_settings = self.load_settings()

        # overwrite settings over old ones
        updated_settings = {**old_settings, **settings}

        # write settings.json in plugin folder
        try:
            with open(settings_file_path, "w") as json_file:
                json.dump(updated_settings, json_file, indent=4)
            return updated_settings
        except Exception:
            log.error(f"Unable to save plugin {self._id} settings.")
            log.warning(self.plugin_specific_error_message())
            return {}

    def _create_settings_from_model(self) -> bool:
        # by default, plugin settings are saved inside the plugin folder
        #   in a JSON file called settings.json
        settings_file_path = os.path.join(self._path, "settings.json")

        try:
            model = self.settings_model()
            # if some settings have no default value this will raise a ValidationError
            settings = model().model_dump_json(indent=4)

            # If each field have a default value and the model is correct,
            # create the settings.json with default values
            with open(settings_file_path, "x") as json_file:
                json_file.write(settings)
                log.debug(
                    f"{self.id} have no settings.json, created with settings model default values"
                )

            return True

        except ValidationError:
            log.debug(
                f"{self.id} settings model have missing defaut values, no settings.json created"
            )
            return False

    def _load_manifest(self):
        plugin_json_metadata_file_name = "plugin.json"
        plugin_json_metadata_file_path = os.path.join(
            self._path, plugin_json_metadata_file_name
        )
        meta = {"id": self._id}
        json_file_data = {}

        if os.path.isfile(plugin_json_metadata_file_path):
            try:
                json_file = open(plugin_json_metadata_file_path)
                json_file_data = json.load(json_file)
                json_file.close()
            except Exception:
                log.debug(
                    f"Loading plugin {self._path} metadata, defaulting to generated values"
                )

        meta["name"] = json_file_data.get("name", to_camel_case(self._id))
        meta["description"] = json_file_data.get(
            "description",
            (
                "Description not found for this plugin. "
                f"Please create a `{plugin_json_metadata_file_name}`"
                " in the plugin folder."
            ),
        )
        meta["author_name"] = json_file_data.get("author_name", "Unknown author")
        meta["author_url"] = json_file_data.get("author_url", "")
        meta["plugin_url"] = json_file_data.get("plugin_url", "")
        meta["tags"] = json_file_data.get("tags", "unknown")
        meta["thumb"] = json_file_data.get("thumb", "")
        meta["version"] = json_file_data.get("version", "0.0.1")
        meta["min_cat_version"] = json_file_data.get("min_cat_version", "")
        meta["max_cat_version"] = json_file_data.get("max_cat_version", "")

        return meta

    def _install_requirements(self):
        req_file = os.path.join(self.path, "requirements.txt")
        filtered_requirements = []

        if os.path.exists(req_file):
            installed_packages = {x.name for x in importlib.metadata.distributions()}

            try:
                with open(req_file, "r") as read_file:
                    requirements = read_file.readlines()

                for req in requirements:
                    log.info(f"Installing requirements for plugin {self.id}")

                    # get package name
                    package_name = Requirement(req).name

                    # check if package is installed
                    if package_name not in installed_packages:
                        filtered_requirements.append(req)
                    else:
                        log.debug(f"{package_name} is already installed")

            except Exception:
                log.error(f"Error during requirements checks for plugin {self.id}")

            if len(filtered_requirements) == 0:
                return

            with tempfile.NamedTemporaryFile(mode="w") as tmp:
                tmp.write("".join(filtered_requirements))
                # If flush is not performed, when pip reads the file it is empty
                tmp.flush()

                try:
                    subprocess.run(
                        ["pip", "install", "--no-cache-dir", "-r", tmp.name], check=True
                    )
                except subprocess.CalledProcessError:
                    log.error(f"Error while installing plugin {self.id} requirements.")

                    # Uninstall the previously installed packages
                    log.info(f"Uninstalling requirements for plugin {self.id}")
                    subprocess.run(["pip", "uninstall", "-r", tmp.name], check=True)

                    raise Exception(f"Error during plugin {self.id} requirements installation")

    # lists of hooks and tools
    def _load_decorated_functions(self):
        hooks = []
        tools = []
        forms = []
        endpoints = []
        plugin_overrides = []

        for py_file in self.py_files:
            py_filename = py_file.replace(".py", "").replace("/", ".")

            log.debug(f"Import module {py_filename}")

            # save a reference to decorated functions
            try:
                plugin_module = importlib.import_module(py_filename)

                hooks += getmembers(plugin_module, self._is_cat_hook)
                tools += getmembers(plugin_module, self._is_cat_tool)
                forms += getmembers(plugin_module, self._is_cat_form)
                endpoints += getmembers(plugin_module, self._is_custom_endpoint)
                plugin_overrides += getmembers(
                    plugin_module, self._is_cat_plugin_override
                )
            except Exception:
                log.error(
                    f"Error in {py_filename}. Unable to load plugin {self._id}"
                )
                log.warning(self.plugin_specific_error_message())

        # clean and enrich instances
        self._hooks = list(map(self._clean_hook, hooks))
        self._tools = list(map(self._clean_tool, tools))
        self._forms = list(map(self._clean_form, forms))
        self._endpoints = list(map(self._clean_endpoint, endpoints))
        self._plugin_overrides = {override.name: override for override in list(map(self._clean_plugin_override, plugin_overrides))}


    def plugin_specific_error_message(self):
        name = self.manifest.get("name")
        url = self.manifest.get("plugin_url")

        if url:
            return f"To resolve any problem related to {name} plugin, contact the creator using github issue at the link {url}"
        return f"Error in {name} plugin, contact the creator"

    def _deactivate_endpoints(self):

        for endpoint in self._endpoints:
            endpoint.deactivate()
        self._endpoints = []

    def _clean_hook(self, hook: CatHook):
        # getmembers returns a tuple
        h = hook[1]
        h.plugin_id = self._id
        return h

    def _clean_tool(self, tool: CatTool):
        # getmembers returns a tuple
        t = tool[1]
        t.plugin_id = self._id
        return t

    def _clean_form(self, form: CatForm):
        # getmembers returns a tuple
        f = form[1]
        f.plugin_id = self._id
        return f
    
    def _clean_endpoint(self, endpoint: CustomEndpoint):
        # getmembers returns a tuple
        f = endpoint[1]
        f.plugin_id = self._id
        return f

    def _clean_plugin_override(self, plugin_override):
        # getmembers returns a tuple
        return plugin_override[1]

    # a plugin hook function has to be decorated with @hook
    # (which returns an instance of CatHook)
    @staticmethod
    def _is_cat_hook(obj):
        return isinstance(obj, CatHook)

    @staticmethod
    def _is_cat_form(obj):
        if not isclass(obj) or obj is CatForm:
            return False

        if not issubclass(obj, CatForm) or not obj._autopilot:
            return False

        return True

    # a plugin tool function has to be decorated with @tool
    # (which returns an instance of CatTool)
    @staticmethod
    def _is_cat_tool(obj):
        return isinstance(obj, CatTool)

    # a plugin override function has to be decorated with @plugin
    # (which returns an instance of CatPluginDecorator)
    @staticmethod
    def _is_cat_plugin_override(obj):
        return isinstance(obj, CatPluginDecorator)

    # a plugin custom endpoint has to be decorated with @endpoint
    # (which returns an instance of CustomEndpoint)
    @staticmethod
    def _is_custom_endpoint(obj):
        return isinstance(obj, CustomEndpoint)
    
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

    @property
    def forms(self):
        return self._forms

    @property
    def endpoints(self):
        return self._endpoints
    
    @property
    def overrides(self):
        return self._plugin_overrides
