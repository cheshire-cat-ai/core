import glob
import time
import shutil
import os
import traceback
import cat.utils as utils
from copy import deepcopy
from cat.log import log
from cat.db import crud
from cat.db.models import Setting
from cat.mad_hatter.plugin_extractor import PluginExtractor
from cat.mad_hatter.plugin import Plugin

# This class is responsible for plugins functionality:
# - loading
# - prioritizing
# - executing
class MadHatter:
    # loads and execute plugins
    # - enter into the plugin folder and loads everthing
    #   that is decorated or named properly
    # - orders plugged in hooks by name and priority
    # - exposes functionality to the cat

    def __init__(self, ccat):
        self.ccat = ccat

        self.plugins = {} # plugins dictionary

        self.hooks = {} # dict of active plugins hooks ( hook_name -> [CatHook, CatHook, ...]) 
        self.tools = [] # list of active plugins tools 

        self.active_plugins = []

        self.plugins_folder = utils.get_plugins_path()

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

        if self.plugin_exists(plugin_id):

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
        all_plugin_folders = [core_plugin_folder] + glob.glob(f"{self.plugins_folder}*/")

        log.info("ACTIVE PLUGINS:")
        log.info(self.active_plugins)

        # discover plugins, folder by folder
        for folder in all_plugin_folders:
            self.load_plugin(folder)

            plugin_id = os.path.basename(os.path.normpath(folder))
            
            if plugin_id in self.active_plugins:
                self.plugins[plugin_id].activate()

        self.sync_hooks_and_tools()

    def load_plugin(self, plugin_path):
        # Instantiate plugin.
        #   If the plugin is inactive, only manifest will be loaded
        #   If active, also settings, tools and hooks
        try:
            plugin = Plugin(plugin_path)
            # if plugin is valid, keep a reference
            self.plugins[plugin.id] = plugin
        except Exception as e:
            # Something happened while loading the plugin.
            # Print the error and go on with the others.
            log.error(str(e))

    # Load hooks and tools of the active plugins into MadHatter 
    def sync_hooks_and_tools(self):

        # emptying tools and hooks
        self.hooks = {}
        self.tools = []

        for _, plugin in self.plugins.items():
            # load hooks and tools
            if plugin.id in self.active_plugins:

                # fix tools so they have an instance of the cat # TODO: make the cat a singleton
                for t in plugin.tools:
                    # Prepare the tool to be used in the Cat (setting the cat instance, adding properties)
                    t.augment_tool(self.ccat)

                # cache tools
                self.tools += plugin.tools

                # cache hooks (indexed by hook name)
                for h in plugin.hooks:
                    if h.name not in self.hooks.keys():
                        self.hooks[h.name] = []
                    self.hooks[h.name].append(h)

        # sort each hooks list by priority
        for hook_name in self.hooks.keys():
            self.hooks[hook_name].sort(key=lambda x: x.priority, reverse=True)
                
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
        new_setting = {
            "name": "active_plugins",
            "value": active_plugins
        }
        new_setting = Setting(**new_setting)
        crud.upsert_setting_by_name(new_setting)

    # loops over tools and assign an embedding each. If an embedding is not present in vectorDB, it is created and saved
    def embed_tools(self):

        # retrieve from vectorDB all tool embeddings
        embedded_tools = self.ccat.memory.vectors.procedural.get_all_points()

        # easy acces to (point_id, tool_description)
        embedded_tools_ids = [t.id for t in embedded_tools]
        embedded_tools_descriptions = [t.payload["page_content"] for t in embedded_tools]

        # loop over mad_hatter tools
        for tool in self.tools:
            # if the tool is not embedded 
            if tool.description not in embedded_tools_descriptions:
                # embed the tool and save it to DB
                self.ccat.memory.vectors.procedural.add_texts(
                    [tool.description],
                    [{
                        "source": "tool",
                        "when": time.time(),
                        "name": tool.name,
                        "docstring": tool.docstring
                    }],
                )

                log.warning(f"Newly embedded tool: {tool.description}")
        
        # easy access to mad hatter tools (found in plugins)
        mad_hatter_tools_descriptions = [t.description for t in self.tools]

        # loop over embedded tools and delete the ones not present in active plugins
        points_to_be_deleted = []
        for id, descr in zip(embedded_tools_ids, embedded_tools_descriptions):
            # if the tool is not active, it inserts it in the list of points to be deleted
            if descr not in mad_hatter_tools_descriptions:
                log.warning(f"Deleting embedded tool: {descr}")
                points_to_be_deleted.append(id)

        # delete not active tools
        if len(points_to_be_deleted) > 0:
            self.ccat.memory.vectors.vector_db.delete(
                collection_name="procedural",
                points_selector=points_to_be_deleted
            )

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
                self.plugins[plugin_id].activate()
                # Ass the plugin in the list of active plugins
                self.active_plugins.append(plugin_id)

            # update DB with list of active plugins, delete duplicate plugins
            self.save_active_plugins_to_db(list(set(self.active_plugins)))

            # update cache and embeddings     
            self.sync_hooks_and_tools()
            self.embed_tools()

        else:
            raise Exception("Plugin {plugin_id} not present in plugins folder")
        
    # execute requested hook
    def execute_hook(self, hook_name, *args):

        # check if hook is supported
        if hook_name not in self.hooks.keys():
            raise Exception(f"Hook {hook_name} not present in any plugin")
        
        # Hook has no arguments (aside cat)
        #  no need to pipe
        if len(args) == 0:
            for hook in self.hooks[hook_name]:
                try:
                    log.debug(f"Executing {hook.plugin_id}::{hook.name} with priotrity {hook.priority}")
                    hook.function(cat=self.ccat)
                except Exception as e:
                    log.error(f"Error in plugin {hook.plugin_id}::{hook.name}")
                    log.error(e)
                    traceback.print_exc()
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
                log.debug(f"Executing {hook.plugin_id}::{hook.name} with priotrity {hook.priority}")
                tea_spoon = hook.function(
                    deepcopy(tea_cup),
                    *deepcopy(args[1:]),
                    cat=self.ccat
                )
                #log.debug(f"Hook {hook.plugin_id}::{hook.name} returned {tea_spoon}")
                if tea_spoon is not None:
                    tea_cup = tea_spoon
            except Exception as e:
                log.error(f"Error in plugin {hook.plugin_id}::{hook.name}")
                log.error(e)
                traceback.print_exc()

        # tea_cup has passed through all hooks. Return final output
        return tea_cup