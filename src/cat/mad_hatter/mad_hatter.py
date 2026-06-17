import os
import inspect
import glob
import shutil
from typing import List, Dict, Any, Callable, Type, Union, TYPE_CHECKING

from cat import log, paths, utils
from cat.env import get_env
from cat.db import DB
from cat.mad_hatter.plugin_extractor import PluginExtractor
from cat.mad_hatter.registry import registry_download_plugin
from cat.mad_hatter.plugin import Plugin

if TYPE_CHECKING:
    from cat.looking_glass.cheshire_cat import CheshireCat
    from cat.services.service import Service
    from cat.mad_hatter.decorators import (
        Hook,
        Tool,
        Endpoint
    )


class MadHatter:
    """Plugin manager."""

    def __init__(self):

        # plugins dictionary, contains all of them (active and inactive)
        # it is kept in sync with the contents of plugin folders
        # for a list of active plugins (stored in db), see MadHatter.get_active_plugins
        self.plugins: Dict[str, Plugin] = {}

        # caches for decorated functions
        self.hooks: Dict[str, List[Hook]] = {}
        self.tools: List[Tool] = []
        self.endpoints: List[Endpoint] = []
        self.service_classes: Dict[str, Dict[str, Type[Service]]] = {}

        # callback out of the hook system to notify other components about a refresh
        self.on_refresh_callbacks: List[Callable] = []

        #self._ensure_plugins_path_importable()


    #def _ensure_plugins_path_importable(self):
    #    """Let plugins import each other constructs."""
    #    
    #    init_file = os.path.join(paths.PLUGINS_PATH, "__init__.py")
    #    if not os.path.exists(init_file):
    #        with open(init_file, "w") as f:
    #            f.write("# Do not remove this file, it makes the plugins folder importable.\n")
    #
    #    plugins_parent = os.path.dirname(paths.PLUGINS_PATH)
    #    if plugins_parent not in os.sys.path:
    #        os.sys.path.insert(0, plugins_parent)

    async def install_plugin(self, plugin_origin, activate=True) -> Plugin:
        """
        Install a plugin.
        
        Parameters
        ----------
        plugin_origin : str
            Path to the plugin zip/tar file or registry URL
        activate : bool, optional
            Whether to activate the plugin after installation. Default is True.
    
        Returns
        -------
        Plugin
            Installed plugin object.
        """
        
        try:
            if plugin_origin.startswith("http"):
                plugin_zip_path = await registry_download_plugin(plugin_origin)
            else:
                plugin_zip_path = plugin_origin

            # extract zip/tar file into plugin folder
            extractor = PluginExtractor(plugin_zip_path)
            plugin_path = extractor.extract(paths.PLUGINS_PATH)

            # remove zip after extraction
            shutil.rmtree(plugin_zip_path, ignore_errors=True)

            # create plugin obj
            plugin = Plugin(plugin_path)
            self.plugins[plugin.id] = plugin
        except Exception as e:
            log.error("Could not install plugin in {plugin_path}. Removing it.")
            shutil.rmtree(plugin_path, ignore_errors=True)
            raise e

        if activate:
            await self.toggle_plugin(plugin.id)
    
        return plugin

    async def uninstall_plugin(self, plugin_id):

        # plugin exists and it is not a core plugin
        if not self.plugin_exists(plugin_id):
            raise Exception(f"Plugin {plugin_id} is not installed")

        # deactivate plugin if it is active (will sync cache)
        if plugin_id in await self.get_active_plugins():
            await self.toggle_plugin(plugin_id)

        # remove plugin from cache
        plugin_path = self.plugins[plugin_id].path
        del self.plugins[plugin_id]

        # remove plugin folder
        shutil.rmtree(plugin_path, ignore_errors=True)

    async def preinstall_plugins(self):
        """
        Preinstall plugins based on env CCAT_PREINSTALLED_PLUGINS.
        Called by CheshireCat during bootstrap.
        Will only run if there are no active plugins.
        """

        active_plugins = await self.get_active_plugins()
        if len(active_plugins) > 0:
            log.info("Plugins already present, skipping preinstallation.")
            return

        preinstalled_plugins = get_env("CCAT_PREINSTALLED_PLUGINS")
        if preinstalled_plugins:
            for location in preinstalled_plugins.split(","):
                location = location.strip()
                try:
                    if location.startswith("http") or location.endswith((".zip", ".tar", ".tar.gz")):
                        # install plugin from url or zip/tar file
                        log.info(f"Preinstalling plugin from {location}")
                        await self.install_plugin(location)
                    else:
                        # plugin already in plugins folder, just save it as active
                        log.info(f"Preactivating plugin {location}")
                        active_plugins = await self.get_active_plugins()
                        plugin_code_is_present = os.path.exists( os.path.join(paths.PLUGINS_PATH, location))
                        if location not in active_plugins and plugin_code_is_present:
                            active_plugins.append(location)
                            await self.set_active_plugins(active_plugins)
                except Exception as e:
                    log.error(f"Error preinstalling plugin {location}: {e}")

    async def find_plugins(self):
        """
        Discover plugins in the plugins folder, activate the ones
        marked as active in the db, and refresh caches.
        """
        # emptying plugin dictionary, plugins will be discovered from disk
        # and stored in a dictionary plugin_id -> plugin_obj
        self.plugins = {}

        # plugins are found in the `./plugins` folder
        all_plugin_folders = glob.glob( f"{paths.PLUGINS_PATH}/*/")

        # active plugins ids (stored in db)
        active_plugins = await self.get_active_plugins()

        # TODOV2: if there is a mismatch between active plugins in db
        #  and plugins found on disk, sync the db
        log.info("Active Plugins:")
        log.info(active_plugins)

        # discover plugins, folder by folder
        for folder in all_plugin_folders:
            try:
                plugin = Plugin(folder)
                self.plugins[plugin.id] = plugin
                if plugin.id in active_plugins:
                    plugin.activate()
            except Exception:
                log.error(f"Could not load plugin in {folder}")

        await self.refresh_caches()

    async def refresh_caches(self):
        """Load decorated functions from active plugins into MadHatter."""
        
        # emptying caches
        self.hooks = {}
        self.tools = []
        self.endpoints = []
        self.service_classes = {}

        for _, plugin in self.plugins.items():
            # load decorated funcs from plugins (only active ones have them populated)
            self.tools += plugin.tools
            self.endpoints += plugin.endpoints

            # index service classes by type and slug
            for S in plugin.services:
                if S.service_type not in self.service_classes.keys():
                    self.service_classes[S.service_type] = {}
                self.service_classes[S.service_type][S.slug] = S
            
            # index hooks by name
            for h in plugin.hooks:
                if h.name not in self.hooks.keys():
                    self.hooks[h.name] = []
                self.hooks[h.name].append(h)

        # sort each hooks list by priority
        for hook_name in self.hooks.keys():
            self.hooks[hook_name].sort(key=lambda x: x.priority, reverse=True)

        # Notify subscribers about finished refresh
        for callback in self.on_refresh_callbacks:
            await utils.run_sync_or_async(callback)

    def plugin_exists(self, plugin_id) -> bool:
        """Check if a plugin exists locally."""
        return plugin_id in self.plugins.keys()

    async def get_active_plugins(self):
        """Get list of active plugins from DB."""
        return await DB.load("active_plugins", default=[])

    async def set_active_plugins(self, active_plugins):
        """Set DB list of active plugins."""
        await DB.save("active_plugins", list(set(active_plugins)))

    async def toggle_plugin(self, plugin_id):
        """Activate / deactivate a plugin."""

        if not self.plugin_exists(plugin_id):
            raise Exception(f"Plugin {plugin_id} not present in plugins folder")

        active_plugins = await self.get_active_plugins()
        plugin_is_active = plugin_id in active_plugins

        # update list of active plugins
        if plugin_is_active:
            log.warning(f"Toggle plugin {plugin_id}: Deactivate")

            # Deactivate the plugin
            self.plugins[plugin_id].deactivate()
            # Remove the plugin from the list of active plugins
            active_plugins.remove(plugin_id)
        else:
            log.warning(f"Toggle plugin {plugin_id}: Activate")

            # Activate the plugin
            try:
                self.plugins[plugin_id].activate()
                # Add the plugin in the list of active plugins
                active_plugins.append(plugin_id)
            except Exception as e:
                # Couldn't activate the plugin
                raise e

        # update DB with list of active plugins, delete duplicate plugins
        await self.set_active_plugins(active_plugins)
        # update cache
        await self.refresh_caches()


    async def execute_hook(
        self, hook_name: str, default_value: Any, caller: Union["CheshireCat", "Service", Callable]
    ) -> Any:
        """
        Execute a hook with the given caller context.

        Parameters
        ----------
        hook_name : str
            Name of the hook to execute.
        default_value : Any
            Default value passed through hooks.
        caller : Union[CheshireCat, Service, Callable]
            The caller (CheshireCat or Service instance) passed directly to hooks.

        Returns
        -------
        Any
            The value after all hooks have been executed.
        """

        # check if hook is supported
        if hook_name not in self.hooks.keys():
            log.debug(f"Hook {hook_name} not present in any plugin")
            return default_value

        # Hook with arguments.
        #  First argument is passed to `execute_hook` is the pipeable one.
        #  Plugins can mutate value and caller in place, or return a new value.
        value = default_value

        # run hooks
        for hook in self.hooks[hook_name]:
            try:
                log.debug(
                    f"Executing {hook.plugin_id}::{hook.name} with priority {hook.priority}"
                )
                returned = await utils.run_sync_or_async(
                    hook.function,
                    value,
                    caller,
                )
                if returned is not None:
                    value = returned
            except Exception:
                log.error(f"Error in plugin {hook.plugin_id}::{hook.name}")
                plugin_obj = self.plugins[hook.plugin_id]
                log.warning(plugin_obj.plugin_specific_error_message())

        # value has passed through all hooks. Return final output
        return value


    def get_plugin(self) -> Plugin:
        """Internal use only. Services should use `self.plugin`."""

        stack = inspect.stack()
        norm_plugins_path = os.path.normpath(paths.PLUGINS_PATH)

        for frame_info in stack:

            frame = frame_info.frame
            module = inspect.getmodule(frame)

            if module and hasattr(module, '__file__'):
                
                abs_path = os.path.abspath(module.__file__)
                if abs_path.startswith(norm_plugins_path + os.sep):
                    plugin_suffix = os.path.relpath(abs_path, norm_plugins_path)
                    plugin_name = plugin_suffix.split(os.sep)[0]
                    if plugin_name in self.plugins:
                        return self.plugins[plugin_name]
                    
        raise Exception("No calling plugin found in the call stack.")
