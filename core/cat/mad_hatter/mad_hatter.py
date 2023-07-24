import glob
import json
import time
import shutil
import os
from typing import Dict

from cat.log import log
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
        self.find_plugins()

    def install_plugin(self, package_plugin):

        # extract zip/tar file into plugin folder
        plugin_folder = self.ccat.get_plugin_path()
        pkg_obj = Package(package_plugin)
        pkg_obj.unpackage(plugin_folder)
        
        self.find_plugins()
        self.embed_tools()

    def uninstall_plugin(self, plugin_id):

        # remove plugin folder
        shutil.rmtree(self.ccat.get_plugin_path() + plugin_id)

     
        self.find_plugins()
        self.embed_tools()

    # discover all plugins
    def find_plugins(self):

        # plugins will be discovered from disk
        #   and stored in a dictionary plugin_id -> plugin_obj
        self.plugins = {}

        # here we keep a cache of found tools and hooks
        self.hooks = []
        self.tools = []

        # plugins are found in the plugins folder,
        #   plus the default core plugin
        #   (where default hooks and tools are defined)
        core_folder = "cat/mad_hatter/core_plugin/"
        plugin_folders = [core_folder] + glob.glob("cat/plugins/*/")
        # TODO: use cat.get_plugin_path() so it can be mocked from tests

        # discover plugins, folder by folder
        for folder in plugin_folders:
            plugin = Plugin(folder)
            # if plugin is valid, keep a reference
            plugin_is_valid = (len(plugin.tools) > 0) or (len(plugin.hooks) > 0)
            if plugin_is_valid:
                self.plugins[plugin.id] = plugin
                self.hooks += plugin.hooks
                self.tools += plugin.tools

        # sort hooks by priority
        self.hooks.sort(key=lambda x: x.priority, reverse=True)

        # fix tools so they have an instance of the cat # TODO: make the cat a singleton
        for t in self.tools:
            # Prepare the tool to be used in the Cat (setting the cat instance, adding properties)
            t.augment_tool(self.ccat)


    # check if plugin exists
    def plugin_exists(self, plugin_id):
        return plugin_id in self.plugins.keys()


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
            self.plugins[plugin_id].toggle()

        # TODO: sync should happen

    # execute requested hook
    def execute_hook(self, hook_name, *args):
        for h in self.hooks:
            if hook_name == h.name:
                return h.function(*args, cat=self.ccat)

        # every hook must have a default in core_plugin
        raise Exception(f"Hook {hook_name} not present in any plugin")
