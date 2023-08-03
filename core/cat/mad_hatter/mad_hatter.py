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

        active_plugins = self.load_active_plugins_from_db()

        if self.plugin_exists(plugin_id):

            # deactivate plugin if it is active (will sync cache)
            if plugin_id in active_plugins:
                self.toggle_plugin(plugin_id)

            # remove plugin
            del self.plugins[plugin_id]

            # remove plugin folder
            shutil.rmtree(self.ccat.get_plugin_path() + plugin_id)

    # discover all plugins
    def find_plugins(self):

        # emptying plugin dictionary, plugins will be discovered from disk
        # and stored in a dictionary plugin_id -> plugin_obj
        self.plugins = {}

        # plugins are found in the plugins folder,
        # plus the default core plugin s(where default hooks and tools are defined)
        core_plugin_folder = "cat/mad_hatter/core_plugin/"

         # plugin folder is "cat/plugins/" in production, "tests/mocks/mock_plugin_folder/" during tests
        plugins_folder = self.ccat.get_plugin_path()

        all_plugin_folders = [core_plugin_folder] + glob.glob(f"{plugins_folder}*/")
        
        # db contains the list of active plugins
        active_plugins = self.load_active_plugins_from_db()

        log("ACTIVE PLUGINS:", "INFO")
        log(active_plugins, "INFO")

        # discover plugins, folder by folder
        for folder in all_plugin_folders:

            # is the plugin active?
            folder_base = os.path.basename(os.path.normpath(folder))
            is_active = folder_base in active_plugins

            self.load_plugin(folder, is_active)

        self.sync_hook_and_tools()

    def load_plugin(self, plugin_path, active):
        # Instantiate plugin.
        #   If the plugin is inactive, only manifest will be loaded
        #   If active, also settings, tools and hooks
        plugin = Plugin(plugin_path, active=active)
        
        # if plugin is valid, keep a reference
        self.plugins[plugin.id] = plugin

    # Load hooks and tools of the active plugins into MadHatter 
    def sync_hook_and_tools(self):

        # emptying tools and hooks
        self.hooks = []
        self.tools = []

        active_plugins = self.load_active_plugins_from_db()

        for _, plugin in self.plugins.items():
            # load hooks and tools
            if plugin.id in active_plugins:

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
        all_tools_points = self.ccat.memory.vectors.procedural.get_all_points()

        # easy access to plugin tools
        plugins_tools_index = {t.description: t for t in self.tools}

        points_to_be_deleted = []
        
        vector_db = self.ccat.memory.vectors.vector_db

        # loop over vectors
        for record in all_tools_points:
            # if the tools is active in plugins, assign embedding
            try:
                tool_description = record.payload["page_content"]
                plugins_tools_index[tool_description].embedding = record.vector
                # log(plugins_tools_index[tool_description], "WARNING")
            # else delete it
            except Exception as e:
                log(f"Deleting embedded tool: {record.payload['page_content']}", "WARNING")
                points_to_be_deleted.append(record.id)

        if len(points_to_be_deleted) > 0:
            vector_db.delete(
                collection_name="procedural",
                points_selector=points_to_be_deleted
            )

        # loop over tools
        for tool in self.tools:
            # if there is no embedding, create it
            if not tool.embedding:
                # save it to DB
                ids_inserted = self.ccat.memory.vectors.procedural.add_texts(
                    [tool.description],
                    [{
                        "source": "tool",
                        "when": time.time(),
                        "name": tool.name,
                        "docstring": tool.docstring
                    }],
                )

                # retrieve saved point and assign embedding to the Tool
                records_inserted = vector_db.retrieve(
                    collection_name="procedural",
                    ids=ids_inserted,
                    with_vectors=True
                )
                tool.embedding = records_inserted[0].vector

                log(f"Newly embedded tool: {tool.description}", "WARNING")

    # activate / deactivate plugin
    def toggle_plugin(self, plugin_id):
        log(f"toggle plugin {plugin_id}", "WARNING")

        if self.plugin_exists(plugin_id):
            
            # get active plugins from db
            active_plugins = self.load_active_plugins_from_db()

            plugin_is_active = plugin_id in active_plugins

            log(plugin_is_active, "WARNING")

            # update list of active plugins
            if plugin_is_active:
                # Deactivate the plugin
                self.plugins[plugin_id].deactivate()
                # Remove the plugin from the list of active plugins
                active_plugins.remove(plugin_id)
            else:
                # Activate the plugin
                self.plugins[plugin_id].activate()
                # Ass the plugin in the list of active plugins
                active_plugins.append(plugin_id)

            log(plugin_is_active, "WARNING")

            # update DB with list of active plugins, delete duplicate plugins
            self.save_active_plugins_to_db(list(set(active_plugins)))

            # update cache and embeddings     
            self.sync_hook_and_tools()
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
