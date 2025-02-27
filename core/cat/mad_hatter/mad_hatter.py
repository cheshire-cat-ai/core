import os
import glob
import shutil
import inspect
from copy import deepcopy
from typing import List, Dict

from cat.log import log

import cat.utils as utils
from cat.utils import singleton

from cat.db import crud
from cat.db.models import Setting

from cat.mad_hatter.plugin_extractor import PluginExtractor
from cat.mad_hatter.plugin import Plugin
from cat.mad_hatter.decorators.hook import CatHook
from cat.mad_hatter.decorators.tool import CatTool
from cat.mad_hatter.decorators.endpoint import CustomEndpoint

from cat.experimental.form import CatForm


# This class is responsible for plugins functionality:
# - loading
# - prioritizing
# - executing
@singleton
class MadHatter:
    # loads and execute plugins
    # - enter into the plugin folder and loads everything
    #   that is decorated or named properly
    # - orders plugged in hooks by name and priority
    # - exposes functionality to the cat

    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}  # plugins dictionary

        self.hooks: Dict[
            str, List[CatHook]
        ] = {}  # dict of active plugins hooks ( hook_name -> [CatHook, CatHook, ...])
        self.tools: List[CatTool] = []  # list of active plugins tools
        self.forms: List[CatForm] = []  # list of active plugins forms
        self.endpoints: List[CustomEndpoint] = []  # list of active plugins endpoints

        self.active_plugins: List[str] = []

        self.plugins_folder = utils.get_plugins_path()

        # this callback is set from outside to be notified when plugin sync is finished
        self.on_finish_plugins_sync_callback = lambda: None

        self.find_plugins()

    def install_plugin(self, package_plugin):
        # extract zip/tar file into plugin folder
        extractor = PluginExtractor(package_plugin)
        plugin_path = extractor.extract(self.plugins_folder)

        # remove zip after extraction
        os.remove(package_plugin)

        # get plugin id (will be its folder name)
        plugin_id = os.path.basename(plugin_path)

        # create plugin obj
        self.load_plugin(plugin_path)

        # activate it
        self.toggle_plugin(plugin_id)

    def uninstall_plugin(self, plugin_id):
        if self.plugin_exists(plugin_id) and (plugin_id != "core_plugin"):
            # deactivate plugin if it is active (will sync cache)
            if plugin_id in self.active_plugins:
                self.toggle_plugin(plugin_id)

            # remove plugin from cache
            plugin_path = self.plugins[plugin_id].path
            del self.plugins[plugin_id]

            # remove plugin folder
            shutil.rmtree(plugin_path)

    # discover all plugins
    def find_plugins(self):
        # emptying plugin dictionary, plugins will be discovered from disk
        # and stored in a dictionary plugin_id -> plugin_obj
        self.plugins = {}

        self.active_plugins = self.load_active_plugins_from_db()

        # plugins are found in the plugins folder,
        # plus the default core plugin s(where default hooks and tools are defined)
        core_plugin_folder = "cat/mad_hatter/core_plugin/"

        # plugin folder is "cat/plugins/" in production, "tests/mocks/mock_plugin_folder/" during tests
        all_plugin_folders = [core_plugin_folder] + glob.glob(
            f"{self.plugins_folder}*/"
        )

        log.info("Active Plugins:")
        log.info(self.active_plugins)

        # discover plugins, folder by folder
        for folder in all_plugin_folders:
            self.load_plugin(folder)

            plugin_id = os.path.basename(os.path.normpath(folder))

            if plugin_id in self.active_plugins:
                try:
                    self.plugins[plugin_id].activate()
                except Exception as e:
                    # Couldn't activate the plugin -> Deactivate it
                    if plugin_id in self.active_plugins:
                        self.toggle_plugin(plugin_id)
                    raise e

        self.sync_hooks_tools_and_forms()

    def load_plugin(self, plugin_path):
        # Instantiate plugin.
        #   If the plugin is inactive, only manifest will be loaded
        #   If active, also settings, tools and hooks
        try:
            plugin = Plugin(plugin_path)
            # if plugin is valid, keep a reference
            self.plugins[plugin.id] = plugin
        except Exception:
            # Something happened while loading the plugin.
            # Print the error and go on with the others.
            log.error(f"Error while loading plugin from {plugin_path}")

    # Load hooks, tools and forms of the active plugins into MadHatter
    def sync_hooks_tools_and_forms(self):
        # emptying tools, hooks and forms
        self.hooks = {}
        self.tools = []
        self.forms = []
        self.endpoints = []

        for _, plugin in self.plugins.items():
            # load hooks, tools, forms and endpoints from active plugins
            if plugin.id in self.active_plugins:
                # cache tools
                self.tools += plugin.tools

                self.forms += plugin.forms

                self.endpoints += plugin.endpoints

                # cache hooks (indexed by hook name)
                for h in plugin.hooks:
                    if h.name not in self.hooks.keys():
                        self.hooks[h.name] = []
                    self.hooks[h.name].append(h)

        # sort each hooks list by priority
        for hook_name in self.hooks.keys():
            self.hooks[hook_name].sort(key=lambda x: x.priority, reverse=True)

        # notify sync has finished (the Cat will ensure all tools are embedded in vector memory)
        self.on_finish_plugins_sync_callback()

    # check if plugin exists
    def plugin_exists(self, plugin_id):
        return plugin_id in self.plugins.keys()

    def load_active_plugins_from_db(self):
        active_plugins = crud.get_setting_by_name("active_plugins")

        if active_plugins is None:
            active_plugins = []
        else:
            active_plugins = active_plugins["value"]

        # core_plugin is always active
        if "core_plugin" not in active_plugins:
            active_plugins += ["core_plugin"]

        return active_plugins

    def save_active_plugins_to_db(self, active_plugins):
        new_setting = {"name": "active_plugins", "value": active_plugins}
        new_setting = Setting(**new_setting)
        crud.upsert_setting_by_name(new_setting)

    # activate / deactivate plugin
    def toggle_plugin(self, plugin_id):
        if self.plugin_exists(plugin_id):
            plugin_is_active = plugin_id in self.active_plugins

            # update list of active plugins
            if plugin_is_active:
                log.warning(f"Toggle plugin {plugin_id}: Deactivate")

                # Deactivate the plugin
                self.plugins[plugin_id].deactivate()
                # Remove the plugin from the list of active plugins
                self.active_plugins.remove(plugin_id)
            else:
                log.warning(f"Toggle plugin {plugin_id}: Activate")

                # Activate the plugin
                try:
                    self.plugins[plugin_id].activate()
                except Exception as e:
                    # Couldn't activate the plugin
                    raise e

                # Add the plugin in the list of active plugins
                self.active_plugins.append(plugin_id)

            # update DB with list of active plugins, delete duplicate plugins
            self.save_active_plugins_to_db(list(set(self.active_plugins)))

            # update cache and embeddings
            self.sync_hooks_tools_and_forms()

        else:
            raise Exception("Plugin {plugin_id} not present in plugins folder")

    # execute requested hook
    def execute_hook(self, hook_name, *args, cat):
        # check if hook is supported
        if hook_name not in self.hooks.keys():
            raise Exception(f"Hook {hook_name} not present in any plugin")

        # Hook has no arguments (aside cat)
        #  no need to pipe
        if len(args) == 0:
            for hook in self.hooks[hook_name]:
                try:
                    log.debug(
                        f"Executing {hook.plugin_id}::{hook.name} with priority {hook.priority}"
                    )
                    hook.function(cat=cat)
                except Exception:
                    log.error(f"Error in plugin {hook.plugin_id}::{hook.name}")
                    plugin_obj = self.plugins[hook.plugin_id]
                    log.warning(plugin_obj.plugin_specific_error_message())
            return

        # Hook with arguments.
        #  First argument is passed to `execute_hook` is the pipeable one.
        #  We call it `tea_cup` as every hook called will receive it as an input,
        #  can add sugar, milk, or whatever, and return it for the next hook
        tea_cup = deepcopy(args[0])

        # run hooks
        for hook in self.hooks[hook_name]:
            try:
                # pass tea_cup to the hooks, along other args
                # hook has at least one argument, and it will be piped
                log.debug(
                    f"Executing {hook.plugin_id}::{hook.name} with priority {hook.priority}"
                )
                tea_spoon = hook.function(
                    deepcopy(tea_cup), *deepcopy(args[1:]), cat=cat
                )
                # log.debug(f"Hook {hook.plugin_id}::{hook.name} returned {tea_spoon}")
                if tea_spoon is not None:
                    tea_cup = tea_spoon
            except Exception:
                log.error(f"Error in plugin {hook.plugin_id}::{hook.name}")
                plugin_obj = self.plugins[hook.plugin_id]
                log.warning(plugin_obj.plugin_specific_error_message())

        # tea_cup has passed through all hooks. Return final output
        return tea_cup

    # get plugin object (used from within a plugin)
    # TODO: should we allow to take directly another plugins' obj?
    # TODO: throw exception if this method is called from outside the plugins folder
    def get_plugin(self):
        # who's calling?
        calling_frame = inspect.currentframe().f_back
        # Get the module associated with the frame
        module = inspect.getmodule(calling_frame)
        # Get the absolute and then relative path of the calling module's file
        abs_path = inspect.getabsfile(module)
        rel_path = os.path.relpath(abs_path)
        # Replace the root and get only the current plugin folder
        plugin_suffix = rel_path.replace(utils.get_plugins_path(), "")
        # Plugin's folder
        name = plugin_suffix.split("/")[0]
        return self.plugins[name]

    @property
    def procedures(self):
        return self.tools + self.forms
