import glob
import json
import time
import shutil
import os
from typing import Dict

from cat.log import log
from cat.db import crud
from cat.db.models import Setting
from cat.infrastructure.package import Package
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

        self.hooks = [] # list of active plugins hooks 
        self.tools = [] # list of active plugins tools 

        self.active_plugins = []

        self.find_plugins()

    def install_plugin(self, package_plugin):

        # extract zip/tar file into plugin folder
        plugin_folder = self.ccat.get_plugin_path()
        archive = Package(package_plugin)
        extracted_contents = archive.unpackage(plugin_folder)
        
        # there should be a method to check for plugin integrity
        if len(extracted_contents) != 1:
            raise Exception("A plugin should consist in one new folder: "
                            "found many contents in compressed archive or plugin already present.")
        
        plugin_id = extracted_contents[0]
        plugin_path = os.path.join(plugin_folder, plugin_id)
        
        if not os.path.isdir(plugin_path):
            raise Exception("A plugin should contain a folder, found a file")

        # create plugin obj
        self.load_plugin(plugin_path, active=False)

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
        plugins_folder = self.ccat.get_plugin_path()

        all_plugin_folders = [core_plugin_folder] + glob.glob(f"{plugins_folder}*/")

        log("ACTIVE PLUGINS:", "INFO")
        log(self.active_plugins, "INFO")

        # discover plugins, folder by folder
        for folder in all_plugin_folders:

            # is the plugin active?
            folder_base = os.path.basename(os.path.normpath(folder))
            is_active = folder_base in self.active_plugins

            self.load_plugin(folder, is_active)

        self.sync_hooks_and_tools()

    def load_plugin(self, plugin_path, active):
        # Instantiate plugin.
        #   If the plugin is inactive, only manifest will be loaded
        #   If active, also settings, tools and hooks
        try:
            plugin = Plugin(plugin_path, active=active)
            # if plugin is valid, keep a reference
            self.plugins[plugin.id] = plugin
        except Exception as e:
            log(e, "WARNING") 

    # Load hooks and tools of the active plugins into MadHatter 
    def sync_hooks_and_tools(self):

        # emptying tools and hooks
        self.hooks = []
        self.tools = []

        for _, plugin in self.plugins.items():
            # load hooks and tools
            if plugin.id in self.active_plugins:

                # fix tools so they have an instance of the cat # TODO: make the cat a singleton
                for t in plugin.tools:
                    # Prepare the tool to be used in the Cat (setting the cat instance, adding properties)
                    t.augment_tool(self.ccat)

                self.hooks += plugin.hooks
                self.tools += plugin.tools

        # sort hooks by priority
        self.hooks.sort(key=lambda x: x.priority, reverse=True)
                
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

                log(f"Newly embedded tool: {tool.description}", "WARNING")
        
        # easy access to mad hatter tools (found in plugins)
        mad_hatter_tools_descriptions = [t.description for t in self.tools]

        # loop over embedded tools and delete the ones not present in active plugins
        points_to_be_deleted = []
        for id, descr in zip(embedded_tools_ids, embedded_tools_descriptions):
            # if the tool is not active, it inserts it in the list of points to be deleted
            if descr not in mad_hatter_tools_descriptions:
                log(f"Deleting embedded tool: {descr}", "WARNING")
                points_to_be_deleted.append(id)

        # delete not active tools
        if len(points_to_be_deleted) > 0:
            self.ccat.memory.vectors.vector_db.delete(
                collection_name="procedural",
                points_selector=points_to_be_deleted
            )

    # activate / deactivate plugin
    def toggle_plugin(self, plugin_id):
        log(f"toggle plugin {plugin_id}", "WARNING")

        if self.plugin_exists(plugin_id):

            plugin_is_active = plugin_id in self.active_plugins

            # update list of active plugins
            if plugin_is_active:
                # Deactivate the plugin
                self.plugins[plugin_id].deactivate()
                # Remove the plugin from the list of active plugins
                self.active_plugins.remove(plugin_id)
            else:
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
        for h in self.hooks:
            if hook_name == h.name:
                return h.function(*args, cat=self.ccat)

        # every hook must have a default in core_plugin
        raise Exception(f"Hook {hook_name} not present in any plugin")
